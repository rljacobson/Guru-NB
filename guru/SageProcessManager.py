import os, time, json
import requests

# from sagenb.notebook.worksheet import Worksheet
# from sagenb.notebook.cell import Cell

from guru.ServerConfigurations import ServerConfigurations
from guru.globals import GURU_NOTEBOOK_DIR, guru_notebook

from sagenb.notebook.worksheet import Worksheet

# A server session is a data structure that keeps track of connections to
# notebook servers. A server session may have many worksheets associated to it.
# A session looks like this:
# a = {"session": session,  # A requests.session object.
#      "mirrors": worksheet_mirrors,  # A Python list of worksheets connected to this session.
#      "server": server  # The server configuration associated to the session (described in ServerConfigurations.py).
#      }

ServerSessions = []

# A worksheet mirror is a data structure describing the relationship of a
# local worksheet to a worksheet on the server. It has the following structure:

# b = {"worksheet": worksheet,  # A local worksheet object.
#      "filename": remote_filename, # The filename of the REMOTE mirror (i.e. rjacobson/37).
#      "name": remote_name  # The title Guru assigned to the REMOTE mirror.
#     }

# ManagedWorksheets is a dictionary with worksheets as keys and and server configurations as values.

ManagedWorksheets = {}

# These are the commands that we handle ONLY on the backend.
UnmirroredCommands = [
    "interrupt",
    "eval",
    "introspect",
    "quit_sage",
    "cell_update" #Required because r['status'] is determined according to if the cell is in a compute queue.
]

def setWorksheetProcessServer(worksheet, server_config=None):
    # sagenb.notebook.worksheet.Worksheet was designed to get it's sage process
    # from its associated notebook, so we have to do some stuff that isn't
    # necessarily how one would normally design it if one were starting
    # from scratch.

    #We will need the worksheet to have it's _notebook property set.
    if (not hasattr(worksheet, "_notebook")) or (worksheet._notebook is None):
        worksheet._notebook = guru_notebook

    #If we aren't given a server config, use the default.
    if not server_config:
        server_config = ServerConfigurations.getDefault()

    # Note that some Sage interfaces do not require worksheet.initialize_sage().
    # Seems to me initialize_sage() doesn't belong in Worksheet at all, but in
    # sagenb.interfaces.worksheet_process.WorksheetProcess, but I didn't write it.

    if server_config["type"]=="local":
        #For local servers, it's easy.
        worksheet = stopSageProcess(worksheet)
        worksheet._Worksheet__sage = getLocalProcess(server_config)
        worksheet.initialize_sage()

    elif server_config["type"]=="notebook server":
        worksheet = setNotebookProcessServer(worksheet, server_config)

    elif server_config["type"]=="cell server":
        pass

    elif server_config["type"]=="remote":
        pass

    else:
        #This should never execute. It just restarts sage using whatever the notebook gives it.
        worksheet.restart_sage()

    return worksheet

def getLocalProcess(server):
    from sagenb.interfaces import WorksheetProcess_ExpectImplementation

    python_command = "%s -python"%server["path"]

    return WorksheetProcess_ExpectImplementation(python=python_command)

def restartSageProcess(worksheet):
    # The code to restart the Sage process in sagenb.notebook.worksheet.Worksheet makes assumptions
    # that may not hold for us.

    if ManagedWorksheets.has_key(worksheet):
        server_config = ManagedWorksheets[worksheet]
    else:
        # We're not managing this worksheet.
        server_config = ServerConfigurations.getDefault()

    #Turns out, the following is equivalent to restarting the process.
    setWorksheetProcessServer(worksheet, server_config)

def stopSageProcess(worksheet, create_new=True):
    #How to stop a process depends on the kind of process.

    if ManagedWorksheets.has_key(worksheet):
        server_config = ManagedWorksheets[worksheet]
    else:
        #We're not managing this worksheet, so assume it's local. It is harmless to do so.
        server_config = {"type": "local"}

    returned_worksheet = worksheet

    if server_config["type"]=="local":
        #The worksheet may not even have a _Worksheet__sage property.
        try:
            worksheet._Worksheet__sage.quit()
        except:
            pass

    elif server_config["type"]=="notebook server":
        #We need to do the following:
        # 1. Sync the remote worksheet with the local worksheet.
        # 2. Remove the mirror from the mirror pool.
        # 3. Delete the remote worksheet.
        # 4. Close the session if there are no other mirrors.
        # 5. Stop managing this worksheet.

        server_session = getSessionForServer(server_config)
        if not server_session:
            #This server has no active sessions, so there's nothing to stop.
            return returned_worksheet

        mirror = getMirrorForWorksheet(worksheet, server_session)
        if not mirror:
            #This worksheet has not yet connected, so nothing to stop.
            return returned_worksheet

        # 1. Sync the remote worksheet with the local worksheet.
        # "Sync" means create a new local worksheet with the contents of the old
        # worksheet and return it. We only do this if create_new is true.
        if create_new:
            new_file = os.path.join(GURU_NOTEBOOK_DIR, "sync_worksheet.sws")
            saveRemoteWorksheet(worksheet, new_file)
            #ws = wsc.notebook.import_worksheet(filename, wsc.notebook_username)
            notebook_username = worksheet.filename().split('/')[0]
            returned_worksheet = worksheet._notebook.import_worksheet(new_file, notebook_username)
            returned_worksheet._notebook = worksheet._notebook
            os.remove(new_file)

        # 2. Remove the mirror from the mirror list.
        server_session["mirrors"].remove(mirror)

        session = server_session["session"]

        # 3. Delete the remote worksheet
        data = {'filename':mirror["filename"]}
        url = "%s/send_to_trash" % ManagedWorksheets[worksheet]["url"]
        response = session.post(url, data)
        #If the server doesn't return '200 OK', raise an exception.
        response.raise_for_status()

        # 4. Close the session if there are no other mirrors.
        if len(server_session["mirrors"]) == 0:
            #Close the requests.session connection.
            session.close()
            ServerSessions.remove(server_session)

        # 5. Stop managing this worksheet.
        del ManagedWorksheets[worksheet]

    elif server_config["type"]=="cell server":
        pass

    elif server_config["type"]=="remote":
        pass

    else:
        pass

    return returned_worksheet

def setNotebookProcessServer(worksheet, server_config):
    # First, stop whatever the worksheet is using.
    worksheet = stopSageProcess(worksheet)

    # Lot's to do in this one:
    # 1. Get an active requests.session object associated to this server.
    #       1.5. If one doesn't exist, create it.
    # 2. Export the local worksheet to an .sws file.
    # 3. Import the .sws file to the Notebook Server.
    # 	    3.5. Record the "filename" of the remote file.
    # 4. Record the mirror information in the mirrors data structure.
    # 5. Set the worksheet to be managed.

    # We are going to construct a new "mirror" as we go along.
    new_mirror = {"worksheet": worksheet}

    # 1. Get an active requests.session object associated to this server.
    server_session = getSessionForServer(server_config)
    # 1.5. If one doesn't exist, create it.
    if not server_session:
        server_session = {}
        server_session["server"] = server_config
        server_session["mirrors"] = []
        # Log in to the server.
        session = connectToNotebookServer(server_config)
        server_session["session"] = session
        ServerSessions.append(server_session)
    else:
        # We're already connected to the server. Get the requests.session object.
        session = server_session["session"]

    # 2. Export the local worksheet to an .sws file.
    file_name = os.path.join(GURU_NOTEBOOK_DIR, "worksheet_mirror.sws")
    if os.path.exists(file_name):
        os.remove(file_name) #This may be unnecessary.
    worksheet._notebook.export_worksheet(worksheet.filename(), file_name)

    # 3. Import the .sws file to the Notebook Server.
    # The URL we need to post to.
    url = "%s/upload_worksheet" % server_config["url"]

    # The name of the remote worksheet.
    # We could do time and date in some format, but this is easy.
    # timestamp = str(int(time.time()))
    #remote_worksheet_name = "%s%s - %s" %(GURU_NOTEBOOK_MIRROR_PREFIX, timestamp, worksheet.name())
    remote_worksheet_name = worksheet.name()
    new_mirror["name"] = remote_worksheet_name

    # Post variables.
    data = {"url":"", "name": remote_worksheet_name}
    # The file we are posting to the server.
    files = {"file": open(file_name, "rb")}
    # Try to send everything to the server.
    response = session.post(url, data, files=files)
    response.raise_for_status()
    # We're done with the file, so close it and delete it.
    files["file"].close()
    os.remove(file_name)

    # If there was a problem with the file we sent, response.url should look like this:
    #   http://localhost:8080/upload_worksheet
    url = response.url
    if url.endswith("upload_worksheet"):
        raise RuntimeError("There was a problem syncing with the remote notebook server.")

    # 3.5. Record the "filename" of the remote file.
    # If the upload was successful, response.url should look something like this:
    #   http://localhost:8080/home/rjacobson/0
    # The "filename" of the remote worksheet is everything between "/home/" and "/alive".
    mirror_filename = url.strip('/').split('/home/')[-1] # Get everything after "/home/".
    #mirror_filename = mirror_filename.split('/alive')[0] # Get everything before "/alive".
    new_mirror["filename"] = mirror_filename

    # 4. Record the mirror information in the mirrors data structure.
    server_session["mirrors"].append(new_mirror)

    # 5. Set the worksheet to be managed.
    ManagedWorksheets[worksheet] = server_config

    return worksheet

def connectToNotebookServer(server_config):
    # Returns a requests.session object.

    # We let the excepts raise where they may.

    session = requests.Session()

    data = {"email": server_config["username"], "password": server_config["password"]}
    url = "%s/login" % server_config["url"]

    response = session.post(url, data)

    #If the server doesn't return '200 OK', raise an exception.
    response.raise_for_status()

    #If the login was unsuccessful, the response.url will still be /login. Otherwise,
    #it will be the user's username.

    url = response.url.strip('/') #Get rid of any trailing /'s.
    username = url.split('/')[-1] #Pick out the username.
    if username == "login":
        #Login must have failed.
        raise RuntimeError("Login failed.")

    return session

def remoteCommand(worksheet, command):
    # Returns a string containing the response of the server.

    # Command is a tuple of the form (command_text, postvars). postvars is NOT json
    # encoded.
    command_text, postvars = command

    if not ManagedWorksheets.has_key(worksheet):
        #We aren't managing this worksheet, so there's nothing to do here.
        return None

    server_config = ManagedWorksheets[worksheet]

    if server_config["type"] == "local":
        #Local processes don't mirror commands, so there's nothing to do here.
        return None

    server_session = getSessionForServer(server_config)
    mirror = getMirrorForWorksheet(worksheet, server_session)

    #Send the command to the server.
    session = server_session["session"]
    url = "%(url)s/home/%(filename)s/%(cmd)s" % {'url':server_config["url"], 'filename':mirror["filename"], 'cmd':command_text}
    # print "MIRRORING AT URL:%s" % url
    if postvars:
        response = session.post(url, postvars)
    else:
        response = session.get(url)

    #If the server doesn't return '200 OK', raise an exception.
    response.raise_for_status()

    #Fix the urls contained in the response.
    from_string = "/home/%s" % mirror["filename"]
    to_string =  "%(url)s/home/%(filename)s" % {'url':server_config["url"], 'filename':mirror["filename"]}
    result = response.text.replace(from_string, to_string)

    return result

def saveRemoteWorksheet(worksheet, filename):

    if not ManagedWorksheets.has_key(worksheet):
        #This is not a managed worksheet. Save the file the normal way.
        worksheet._notebook.export_worksheet(worksheet.filename(), filename)
        return

    server_config = ManagedWorksheets[worksheet]
    if server_config["type"] == "local":
        #This is not a remote worksheet. Save the file the normal way.
        worksheet._notebook.export_worksheet(worksheet.filename(), filename)
        return

    server_session = getSessionForServer(server_config)
    if not server_session:
        #Not connected for some reason. Nothing to do.
        return

    mirror = getMirrorForWorksheet(worksheet, server_session)
    session = server_session["session"]

    #Open a file to write to.
    f = open(filename, 'w')

    #Sanitize the title for use in a url.
    import urllib
    local_title = urllib.quote(mirror["name"])

    #Ask the server for a copy of the file.
    url = "%(url)s/home/%(remote_filename)s/download/%(local_title)s.sws"
    url = url % {"url": server_config["url"], "remote_filename": mirror["filename"], "local_title": local_title}
    response = session.get(url, stream=True)
    for t in response.iter_content():
        f.write(t)

    f.close()

def getSessionCookie(server_config):
    # Returns the session cookie associated to the worksheet, or an empty string if there is none.

    if server_config["type"] != "notebook server":
        #This is not a remote worksheet.  Nothing to return.
        return ''

    server_session = getSessionForServer(server_config)
    if not server_session:
        #Not connected for some reason. Nothing to do.
        return ''

    session = server_session["session"]

    try:
        domain_string = session.cookies["session"]
    except:
        #There is no session cookie. This case shouldn't ever happen.
        return ''

    #We extract the domain from the url of the server.
    #First, remove 'http://' and split on '/'.
    domain_string = server_config["url"][7:].split('/')[0]
    #Now, strip off the port number if there is one.
    domain_string = domain_string.split(':')[0]

    # Construct a cookie string. The string has the form:
    #    'session="0934839894"; domain=localhost.local; path=/'

    cookie_string = 'session=%(session)s; domain=%(domain)s; path=/'
    cookie_string = cookie_string % {"session": session.cookies["session"], "domain": domain_string}

    return cookie_string


def getSessionForServer(server_config):
    #Given a server configuration, returns a session if one exists. Otherwise, returns None.
    for server_session in ServerSessions:
        if server_session["server"] == server_config:
            return server_session

    return None

def getMirrorForWorksheet(worksheet, server_session):
    #Given a worksheet and server_session, returns the mirror associated to the worksheet.
    #If there is no mirror for the worksheet, returns None.
    for mirror in server_session["mirrors"]:
        if mirror["worksheet"] is worksheet:
            return mirror

    return None