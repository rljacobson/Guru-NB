from PySide.QtGui import QDialog

from guru.Ui_Consoles import Ui_Consoles

class Consoles(QDialog, Ui_Consoles):

    def __init__(self, parent=None):
        super(Consoles, self).__init__(parent)
        self.__index=0
        self.setupUi(self)


    def putAjaxMessage(self, text):
        self.ajax_console.append(text)
        #print text


    def putSageProcessMessage(self, text):
        self.sage_console.append(text)

