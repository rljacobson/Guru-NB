############### Sage Server Configurations ###############

# This class encapsulates a list of Sage servers which can provide us with Sage processes.
# The class is static--it is never meant to be instantiated.
# The list is populated in MainWindow.restoreSettings().
# A "Sage server" can be a path to a local Sage installation.

# ServerConfigurations is initialized in MainWindow.restoreSettings(), while ServerListDlg
# is responsible for manipulating the static class. ServerConfigurations is "saved" in
# MainWindow.saveSettings() (which is called when app termination is imminent).

# There are currently two types of server configurations, each having the following
# structure:
#
# a = {"type": "local",
#      "name:": "name of server",
#      "default": False, # A boolean indicating whether it is the default server.
#      "path": "/absolute/path/to/sage"}
# Note: "path" must be the absolute path to the (lowercase 's') sage binary.
#
# b = {"type": "notebook server",
#      "name": "name of server",
#      "default": False, # A boolean indicating whether it is the default server.
#      "username": "username for the notebook server",
#      "password": "password for the notebook server",
#      "url": "http://url.of/the/Sage/Notebook/Server"
#      }
# Note: "url" does not need the "http://", a trailing /, or to end in "/login/", though it can.
#

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
            return ServerConfigurations.server_list[0]
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