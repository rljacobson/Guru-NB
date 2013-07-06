import os, subprocess

from PySide.QtGui import (QApplication, QDialog, QMessageBox, QFileDialog)
from PySide.QtCore import (SIGNAL)

# from Ui_EditSageServerDlg import Ui_EditSageServerDlg
from guru.Ui_EditSageServerDlg import Ui_EditSageServerDlg

class EditSageServerDlg(QDialog, Ui_EditSageServerDlg):
    def __init__(self, parent=None, server_info=None):
        super(EditSageServerDlg, self).__init__(parent)

        self.setupUi(self)

        #If the user changes the path, validate the path. Unfortunately, this doesn't
        #fire in every scenario we'd like, so calls to self.validateServerPath() are
        #peppered throughout the code below.
        self.connect(self.txtPath, SIGNAL("editingFinished()"), self.validateServerPath)
        self.connect(self.btnOpenPath, SIGNAL("clicked()"), self.openPath)


        self.validServer=False

        #In the future, there will be more types of server configurations than just "local."
        self.server_type = "local"

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
                self.validateServerPath()

    def validateServerPath(self):
        #The text of self.txtPath should contain the path to a Sage installation.
        #We attempt to run "sage -version" to test that the installation is valid.

        path = self.txtPath.text().strip()

        if not path:
            self.lblDetectedVersion.setText('')
            self.validServer = False
            return

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
            self.validServer = False
        else:
            self.lblDetectedVersion.setText(out)
            self.validServer = True

    def openPath(self):
        file_name = QFileDialog.getOpenFileName(self, "Select Sage Installation")[0]
        self.txtPath.setText(file_name)
        self.validateServerPath()


    def accept(self, *args, **kwargs):
        #Validate the input, returning if invalid.

        #The configuration name cannot be empty or only whitespace.
        configuration_name = self.txtName.text().strip()
        if not configuration_name:
            QMessageBox.critical(self, "Missing Name", "You must give this server configuration a name.")
            self.txtName.selectAll()
            self.txtName.setFocus()
            return

        self.validateServerPath()
        if not self.validServer:
            QMessageBox.critical(self, "Invalid Path", "The path you entered does not point to a valid Sage installation.")
            self.txtPath.selectAll()
            self.txtPath.setFocus()
            return

        #Input is valid, so accept.
        QDialog.accept(self)

if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)

    dlg = EditSageServerDlg()
    dlg.exec_()