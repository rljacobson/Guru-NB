from PySide.QtGui import (QApplication, QDialog, QMessageBox, QListWidgetItem, QFont)
from PySide.QtCore import (SIGNAL)

# from Ui_ServerListDlg import Ui_ServerListDlg
from guru.Ui_ServerListDlg import Ui_ServerListDlg
# from EditSageServerDlg import EditSageServerDlg
from guru.EditSageServerDlg import EditSageServerDlg
from guru.globals import ServerConfigurations

class ServerListDlg(QDialog, Ui_ServerListDlg):
    def __init__(self, parent=None):
        super(ServerListDlg, self).__init__(parent)

        self.setupUi(self)

        #Hook up the UI.
        self.connect(self.AddServerBtn, SIGNAL("clicked()"), self.addServer)
        self.connect(self.EditBtn, SIGNAL("clicked()"), self.editServer)
        self.connect(self.ServerListView, SIGNAL("itemDoubleClicked(QListWidgetItem*)"), self.editServer)
        # self.connect(self.MoveUpBtn, SIGNAL("clicked()"), self.moveUp)
        # self.connect(self.MoveDownBtn, SIGNAL("clicked()"), self.moveDown)
        self.connect(self.DeleteServerBtn, SIGNAL("clicked()"), self.deleteServer)

        self.populateServerListView()

    def addServer(self):
        dialog = EditSageServerDlg(self)

        name_collision = True #The while loop needs to run at least once.
        while name_collision:
            if not dialog.exec_():
                #The user clicked cancel.
                return

            #Fetch the data.
            new_server = dict()
            new_server["type"] = "local"
            new_server["name"] = dialog.txtName.text()
            new_server["path"] = dialog.txtPath.text()
            new_server["default"] = dialog.DefaultCheckBox.isChecked()

            #Check to see if the name is in use.
            name_collision = ServerConfigurations.getServerByName(new_server["name"])
            #If the user changed the name to a new name that is already in use, name_collision will
            #not be None. The loop will continue and the dialog reopened.
            if name_collision:
                #The name is already in use.
                QMessageBox.critical(self, "Name already exists", "A server configuration already exists with that name. Choose a different name.")
                dialog.txtName.selectAll()
                dialog.txtName.setFocus()

        #Add the server configuration to the list.
        ServerConfigurations.addServer(new_server)
        item = QListWidgetItem(new_server["name"], self.ServerListView)
        self.ServerListView.setCurrentItem(item)
        if new_server["default"]:
            self.updateListViewDefault()

    def editServer(self):
        #Which server configuration is selected?
        if not self.ServerListView.currentItem():
            #Nothing selected.
            return
        name = self.ServerListView.currentItem().text()

        #Find the corresponding
        server_config = ServerConfigurations.getServerByName(name)

        dialog = EditSageServerDlg(server_info=server_config)

        name_collision = True #The while loop needs to run at least once.
        while name_collision:
            if not dialog.exec_():
                #User clicked cancel.
                return

            name_collision = False #We check it with the 'if' below.
            new_name = dialog.txtName.text()
            #If the user changed the name to a new name that is already in use, the loop will continue
            #and the dialog reopened.
            if new_name != server_config["name"] and ServerConfigurations.getServerByName(new_name):
                #The name is already in use.
                name_collision = True
                QMessageBox.critical(self, "Name already exists", "A server configuration already exists with that name. Choose a different name.")
                dialog.txtName.selectAll()
                dialog.txtName.setFocus()

        #Update server_config
        server_config["type"] = dialog.server_type
        server_config["name"] = new_name
        server_config["path"] = dialog.txtPath.text()
        self.ServerListView.currentItem().setText(new_name)

        #When we set the "default" value, we need to also take care of the font of the item in the ListView.
        ServerConfigurations.setDefault(server_config, set=dialog.DefaultCheckBox.isChecked())
        #Update the ListView to reflect our possibly new default server settings.
        self.updateListViewDefault()

    def deleteServer(self):
        #Which server configuration is selected?
        if not self.ServerListView.currentItem():
            #Nothing selected, nothing to do.
            return
        name = self.ServerListView.currentItem().text()

        #Remove the corresponding server from the server_list.
        ServerConfigurations.removeServerByName(name)
        #And remove it from the ListView as well.
        self.removeSelectedItem()

    def removeSelectedItem(self):
        #For some weird reason, we need to do this in order to delete the selected item.
        for item in self.ServerListView.selectedItems():
            self.ServerListView.takeItem(self.ServerListView.row(item))

    def updateListViewDefault(self):
        #This method updates the font weight of the Listview.
        #Bold ONLY the default server in the ListView.
        for j in range(self.ServerListView.count()):
            item = self.ServerListView.item(j)
            if ServerConfigurations.default and item.text() == ServerConfigurations.default["name"]:
                self.setItemFontWeight(item, QFont.Bold)
            else:
                self.setItemFontWeight(item, QFont.Normal)

    def populateServerListView(self):
        #Remove everything from the list. Unnecessary with current design, but eh.
        self.ServerListView.clear()

        #Add each server configuration to the ListView.
        for server in ServerConfigurations.server_list:
            item = QListWidgetItem(server["name"], self.ServerListView)
            if server["default"]:
                #We bold the default server.
                self.setItemFontWeight(item, QFont.Bold)
                self.ServerListView.setCurrentItem(item)

    def setItemFontWeight(self, item, weight):
        #Seems like there should be an easier way to do this.
        font = item.font()
        font.setWeight(weight)
        item.setFont(font)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    dlg = ServerListDlg()
    dlg.exec_()