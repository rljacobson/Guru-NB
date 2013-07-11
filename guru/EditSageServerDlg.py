import os, subprocess

from PySide.QtGui import (QApplication, QDialog, QMessageBox, QFileDialog)
from PySide.QtCore import (SIGNAL)

from guru.Ui_EditSageServerDlg import Ui_EditSageServerDlg

class EditSageServerDlg(QDialog, Ui_EditSageServerDlg):
    def __init__(self, parent=None, server_info=None):
        super(EditSageServerDlg, self).__init__(parent)

        self.setupUi(self)

        #If the user changes the path, validate the path. Unfortunately, this doesn't
        #fire in every scenario we'd like, so calls to self.validateServerPath() are
        #peppered throughout the code below.
        self.connect(self.txtPath, SIGNAL("editingFinished()"), self.validateLocalServerPath)
        self.connect(self.btnOpenPath, SIGNAL("clicked()"), self.openLocalServerPath)
        self.connect(self.TestLoginBtn, SIGNAL("clicked()"), self.validateNotebookServer)

        #server_info is a dictionary with which we populate the controls.
        if server_info is not None:
            #Every type of server has a name.
            self.txtName.setText(server_info["name"])
            #server_info.get("default", False) returns the value if the key "default" exists,
            #otherwise it creates the key-value pair with a value of False and returns False.
            self.DefaultCheckBox.setChecked(server_info.get("default", False))

            if server_info["type"]=="local":
                #If it's a local server (i.e. command line), configure the
                #dialog accordingly.
                self.txtPath.setText(server_info["path"])
                self.validateLocalServerPath()
                self.ServerTypeTabs.setCurrentWidget(self.LocalServerTab)
            elif server_info["type"]=="notebook server":
                self.txtNotebookServerURL.setText(server_info["url"])
                self.txtNotebookServerUsername.setText(server_info["username"])
                self.txtNotebookServerPassword.setText(server_info["password"])
                self.ServerTypeTabs.setCurrentWidget(self.NotbookServerTab)

    def validateLocalServerPath(self):
        #The text of self.txtPath should contain the path to a Sage installation.
        #We attempt to run "sage -version" to test that the installation is valid.

        path = self.txtPath.text().strip()

        if not path:
            self.lblDetectedVersion.setText('')
            return False

        #We let users point to the .app bundle on Mac OS X.
        if path.endswith('.app'):
            #The path to sage under the Sage bundle has the form
            #   /Applications/Sage-5.8-OSX-64bit-10.8.app/Contents/Resources/sage/sage
            path = os.path.join(path, 'Contents', 'Resources', 'sage', 'sage')
            #...and update self.txtPath while we're at it.
            self.txtPath.setText(path)

        cmd = '%s -version'%path
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        p.wait()
        #Capture the output.
        out = p.stdout.read()

        if p.returncode or out[:12]!="Sage Version":
            error_message = "<font color='red'><b>Path does not point to a valid Sage installation.</b></font><br>"
            #Upon error, only report the first 256 characters of the output.
            errout = out + p.stderr.read()
            error_message += errout[:256]
            self.lblDetectedVersion.setText(error_message)
            return False
        else:
            self.lblDetectedVersion.setText(out)
            return True

    def openLocalServerPath(self):
        file_name = QFileDialog.getOpenFileName(self, "Select Sage Installation")[0]
        self.txtPath.setText(file_name)
        self.validateLocalServerPath()

    def validateNotebookServer(self):
        #We try to log in to the Notebook server with the provided credentials.

        import requests
        session = requests.Session()

        #First, we massage the url into the right form.
        url = self.txtNotebookServerURL.text().strip('/') #Get rid of any trailing /'s.
        if not url.lower().startswith("http://"):
            url = "http://" + url
        if not url.endswith("/login"):
            url += "/login"

        data = {"email": self.txtNotebookServerUsername.text(), "password": self.txtNotebookServerPassword.text()}

        succeeded = True

        try:
            response = session.post(url, data)
            #If the server doesn't return '200 OK', raise an exception.
            response.raise_for_status()

            #If the login was unsuccessful, the response.url will still be /login. Otherwise,
            #it will be the user's username.

            # print "POST url: %s" % url
            # print "RESPONSE url: %s"%response.url
            # print "RESPONSE status_code: %s"%response.status_code
            # print "RESPONSE history: %s"%response.history

            url = response.url.strip('/') #Get rid of any trailing /'s.
            username = url.split('/')[-1] #Pick out the username.
            if username == "login":
                #Login must have failed.
                self.TestLoginLbl.setText("<font color='red'>Login Failed. Check username and password.</font>")
                self.txtNotebookServerUsername.selectAll()
                self.txtNotebookServerUsername.setFocus()
                succeeded = False
            else:
                self.TestLoginLbl.setText("<font color='green'>Logged in as %s.</font>"%username)
                succeeded = True
        except Exception as e:
            #Generally, an exception is raised if the server is unreachable or if the url is malformed.
            failed_message = "<font color='red'>Failed to connect to server.</font><br>%s" % e.message
            self.TestLoginLbl.setText(failed_message)
            self.txtNotebookServerURL.selectAll()
            self.txtNotebookServerURL.setFocus()
            succeeded = False
        finally:
            session.close()

        return succeeded

    def accept(self, *args, **kwargs):
        #Validate the input, returning if invalid.

        #The configuration name cannot be empty or only whitespace.
        configuration_name = self.txtName.text().strip()
        if not configuration_name:
            QMessageBox.critical(self, "Missing Name", "You must give this server configuration a name.")
            self.txtName.selectAll()
            self.txtName.setFocus()
            return

        #We check to see if the user entered a valid server configuration.
        if self.ServerTypeTabs.currentWidget() is self.LocalServerTab:
            if not self.validateLocalServerPath():
                QMessageBox.critical(self, "Invalid Path", "The path you entered does not point to a valid Sage installation.")
                self.txtPath.selectAll()
                self.txtPath.setFocus()
                return
        elif self.ServerTypeTabs.currentWidget() is self.NotbookServerTab:
            if not self.validateNotebookServer():
                QMessageBox.critical(self, "Invalid Notebook Server", "The Sage Notebook Server settings you provided are not valid.")
                return


        #Input is valid, so accept.
        QDialog.accept(self)

    def getServerConfiguration(self):
        server_config = dict()
        server_config["name"] = self.txtName.text()
        server_config["default"] = self.DefaultCheckBox.isChecked()

        # This method does all of the work of packaging the settings into a dictionary.
        if self.ServerTypeTabs.currentWidget() is self.LocalServerTab:
            server_config["type"] = "local"
            server_config["path"] = self.txtPath.text()
        elif self.ServerTypeTabs.currentWidget() is self.NotbookServerTab:
            server_config["type"] = "notebook server"

            #We massage the url into the right form.
            url = self.txtNotebookServerURL.text().strip('/') #Get rid of any trailing /'s.
            if not url.lower().startswith("http://"):
                url = "http://" + url
            #strip off the "/login" if it exists.
            if url.endswith("/login"):
                url = url[:-6]
            server_config["url"] = url
            server_config["username"] = self.txtNotebookServerUsername.text()
            server_config["password"] = self.txtNotebookServerPassword.text()

        return server_config

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    dlg = EditSageServerDlg()
    dlg.exec_()