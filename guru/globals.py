import os, sys, tempfile
from pkg_resources import resource_filename


############### Global Constants ###############
#This magic gets the Guru directory.
GURU_ROOT = os.path.split(resource_filename(__name__, ''))[0]
GURU_PORT = 8081 #Not actually constant.
GURU_NOTEBOOK_DIR = os.path.join(tempfile.mkdtemp(), '.sagenb')
GURU_USERNAME = 'admin'
GURU_EMAIL = 'rljacobson@gmail.com'
GURU_ONLINE_DOCUMENTATION = 'http://www.sagemath.org/doc/index.html'
GURU_LIB_PATH = os.path.join(GURU_ROOT, "site-packages")
sys.path.append(GURU_LIB_PATH)

############### Sage Server Configurations ###############

# This class encapsulates a list of Sage servers which can provide us with Sage processes.
# The class is static--it is never meant to be instantiated.
# The list is populated in MainWindow.restoreSettings().
# A "Sage server" can be a path to a local Sage installation.

# ServerConfigurations is initialized in MainWindow.restoreSettings(), while ServerListDlg
# is responsible for manipulating the static class. ServerConfigurations is "saved" in
# MainWindow.saveSettings() (which is called when app termination is imminent).

class ServerConfigurations:
    server_list = []
    default = None

    @staticmethod
    def restoreFromList(list_to_restore):
        #The only extra thing we have to do is set the default server configuration.
        ServerConfigurations.server_list = list_to_restore
        for server in ServerConfigurations.server_list:
            if server["default"]:
                ServerConfigurations.setDefault(server)
                break

    @staticmethod
    def setDefault(default_server, set=True):
        #If set is False, the caller is trying to demote default_server to NOT be default.
        if not set and ServerConfigurations.default is default_server:
            #Demotion is easy.
            default_server["default"] = False
            ServerConfigurations.default = None
            return

        #Set all other server's "default" value to False, default_server's to True.
        for server in ServerConfigurations.server_list:
            if server is default_server:
                server["default"] = True
            else:
                server["default"] = False

        #...and keep track of which is the default.
        ServerConfigurations.default = default_server

    @staticmethod
    def addServer(new_server):
        #We do NOT enforce uniqueness of the server name. The caller should check existence
        #with getServerByName() first before adding.
        ServerConfigurations.server_list.append(new_server)
        if new_server["default"]:
            ServerConfigurations.setDefault(new_server)

    @staticmethod
    def getDefault():
        #The point of getDefault() is that it ALWAYS returns a server (unless of course there are none).
        if ServerConfigurations.default:
            #There is a default, return it.
            return ServerConfigurations.default
        elif ServerConfigurations.server_list:
            #There is no default, but there are servers, so just return the first one in the list.
            ServerConfigurations.server_list[0]
        else:
            #There are no servers to return.
            return None

    @staticmethod
    def getServerByName(name):
        lst = [server for server in ServerConfigurations.server_list if server["name"]==name]
        if lst:
            return lst[0]
        return None

    @staticmethod
    def removeServerByName(name):
        server = ServerConfigurations.getServerByName(name)
        if server is None:
            #No server by that name. Nothing to do.
            return
        #Keep the default up to date.
        if ServerConfigurations.default is server:
            ServerConfigurations.default = None
        ServerConfigurations.server_list.remove(server)

############### Fix sagenb Paths ###############
import sagenb.misc.misc
sagenb.misc.misc.DOT_SAGENB = GURU_NOTEBOOK_DIR

#Should we set the current directory to the user's home directory?
#os.curdir = os.path.expanduser("~")

############### Local Notebook ###############
from sagenb.notebook.notebook import Notebook

guru_notebook = Notebook(GURU_NOTEBOOK_DIR)
guru_notebook.user_manager().add_user(GURU_USERNAME, GURU_USERNAME, GURU_EMAIL,force=True)
guru_notebook.save() #Write out changes to disk. Unnecessary?

############### Cleanup, Utility Functions, etc. ###############

def cleanup():
    if guru_notebook is not None:
        guru_notebook.delete()


guru_server_thread = None
def startServerThread():
    global guru_server_thread
    global guru_notebook
    from threading import Thread
    from guru.RunFlask import startServer

    options = {'notebook_to_use':guru_notebook, 'open_browser': False, 'debug_mode': True}

    guru_server_thread = Thread(target=startServer, kwargs=options)
    #Setting guru_server_thread.daemon to False would keep Python from terminating as long
    #as the thread is executing.
    guru_server_thread.daemon = True
    guru_server_thread.start()
