from sagenb.notebook.worksheet import Worksheet

from guru.ServerConfigurations import ServerConfigurations

def setWorksheetProcessServer(worksheet, server_config=None):
    # sagenb.notebook.worksheet.Worksheet was designed to get it's sage process
    # from its associated notebook, so we have to do some stuff that isn't
    # necessarily how one would normally design it if one were starting
    # from scratch.
    if not server_config:
        server_config = ServerConfigurations.getDefault()

    #worksheet = Worksheet()

    #Stop whatever process the worksheet may currently be running.
    #if hasattr(worksheet, "_Worksheet__sage") and worksheet._Worksheet__sage:
    try:
        worksheet._Worksheet__sage.quit()
    except:
        pass


    # Note that some Sage interfaces do not require worksheet.initialize_sage().
    # Seems to me initialize_sage() doesn't belong in Worksheet at all, but in
    # sagenb.interfaces.worksheet_process.WorksheetProcess, but I didn't write it.

    if server_config["type"]=="local":
        worksheet._Worksheet__sage = getLocalProcess(server_config)
        worksheet.initialize_sage()

    elif server_config["type"]=="cell server":
        pass

    elif server_config["type"]=="notebook server":
        pass

    elif server_config["type"]=="remote":
        pass

    else:
        #This should never execute. It just restarts sage using whatever the notebook gives it.
        worksheet.restart_sage()

def getLocalProcess(server):
    from sagenb.interfaces import WorksheetProcess_ExpectImplementation

    python_command = "%s -python"%server["path"]

    return WorksheetProcess_ExpectImplementation(python=python_command)

def restartSageProcess(worksheet, server_config):
    # The code to restart the Sage process in sagenb.notebook.worksheet.Worksheet makes assumptions
    # that may not hold for us.

    #Turns out, the following is equivalent to restarting the process.
    setWorksheetProcessServer(worksheet, server_config)