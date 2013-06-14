import platform
import os

from PySide.QtGui import (QMainWindow, QMessageBox, QFileDialog)
from PySide.QtCore import (SIGNAL, Slot)

from PySide import __version__ as PYSIDE_VERSION_STR
from PySide.QtCore import __version__ as QT_VERSION_STR

from guru.Ui_MainWindow import Ui_MainWindow
from guru.WebViewController import WebViewController
from guru.WorksheetController import WorksheetController
from guru.Consoles import Consoles

class MainWindow(QMainWindow, Ui_MainWindow):

    #Keep track of the MainWindow objects.
    mainWindows = set()
    
    def __init__(self, parent=None, isWelcome=False):
        super(MainWindow, self).__init__(parent)

        #Add self to the set of open mainWindows.
        MainWindow.mainWindows.add(self)
        self.isQuitting = False

        #This window may be editing a worksheet associated to a file.
        self.filename = None

        #Consoles are just windows displaying logs of various things going on.
        self.consoles_window = Consoles(self) #Hidden until shown.

        #Lazy instantiation. Seems unnecessary at this point, to be honest.
        self._webViewController = None

        #Determines if this is a welcome page window.
        self.isWelcome = isWelcome

        self.setupUi()
    
    def setupUi(self):
        #The superclass sets up most of the UI.
        super(MainWindow, self).setupUi(self)

        self.setUnifiedTitleAndToolBarOnMac(True)

        self.setCentralWidget(self.webViewController().webView())
        #self.__index = 0

        #Connect all the actions.
        #File actions
        self.connect(self.actionNew, SIGNAL("triggered()"), self.doActionNew)
        self.connect(self.actionOpen, SIGNAL("triggered()"), self.doActionOpen)
        self.connect(self.actionSave, SIGNAL("triggered()"), self.doActionSave)
        self.connect(self.actionSaveAs, SIGNAL("triggered()"), self.doActionSaveAs)
        self.connect(self.actionPrint, SIGNAL("triggered()"), self.doActionPrint)
        self.connect(self.actionQuit, SIGNAL("triggered()"), self.doActionQuit)

        #Edit actions
        self.connect(self.actionCopy, SIGNAL("triggered()"), self.doActionCopy)
        self.connect(self.actionCut, SIGNAL("triggered()"), self.doActionCut)
        self.connect(self.actionPaste, SIGNAL("triggered()"), self.doActionPaste)

        #Worksheet actions
        self.connect(self.actionWorksheetProperties, SIGNAL("triggered()"), self.doActionWorksheetProperties)
        self.connect(self.actionEvaluateWorksheet, SIGNAL("triggered()"), self.doActionEvaluateWorksheet)
        self.connect(self.actionInterrupt, SIGNAL("triggered()"), self.doActionInterrupt)

        #Miscellaneous actions
        self.connect(self.actionAbout, SIGNAL("triggered()"), self.doActionAbout)
        self.connect(self.actionSageServer, SIGNAL("triggered()"), self.doActionSageServer)

        if self.isWelcome:
            #Display the welcome screen.
            self.showWelcome()

    def webViewController(self):
        #Why am I creating a new webViewController if there is none?
        if self._webViewController==None:
            self._webViewController = WebViewController(putAjaxConsole = self.consoles_window.putAjaxMessage, putSageConsole = self.consoles_window.putSageProcessMessage)
            #self._webViewController = WebViewController(putAjaxConsole = self.simpleConsole, putSageConsole = self.simpleConsole)

        return self._webViewController

    #Make the UI changes necessary for showing the welcome page.
    def showWelcome(self):
        #This method is only called if we're a welcome page, so...
        self.isWelcome = True
        self.filename = None

        #Hide the toolbar.
        self.toolBar.hide()

        #Disable the relevant actions.
        self.enableEditingActions(False)

        #Display the welcome page.
        self.webViewController().show_rendered_template("html/guru_welcome.html")

        #Hook up the javscript bridge.
        self.webViewController().webView().page().mainFrame().addToJavaScriptWindowObject("GuruWelcome", self)

    #This is the counterpart to showWelcome(). It undoes the UI changes
    #that showWelcome() does. Probably a silly name.
    def hideWelcome(self):
        #We aren't a welcome page anymore.
        self.isWelcome = False
        #Enable the relevant actions.
        self.enableEditingActions()
        #Unhide the toolbar
        self.toolBar.show()

    #The editing actions are only relevant if we are editing a worksheet.
    #Otherwise (i.e. for the welcome page), they should be disabled.
    def enableEditingActions(self, enabling=True):
        self.actionEvaluateWorksheet.setEnabled(enabling)
        self.actionWorksheetProperties.setEnabled(enabling)
        self.actionPaste.setEnabled(enabling)
        self.actionSave.setEnabled(enabling)
        self.actionCut.setEnabled(enabling)
        self.actionSageServer.setEnabled(enabling)
        self.actionCopy.setEnabled(enabling)
        self.actionInterrupt.setEnabled(enabling)
        self.actionPrint.setEnabled(enabling)
        self.actionSaveAs.setEnabled(enabling)


    def showConsoles(self):
        self.consoles_window.show()

    def simpleConsole(self, text):
        print text

    #This method is called whenever the window is closed.
    def closeEvent(self, event):
        shouldClose = False

        if (self.isWelcome == False):
            #If the worksheet is dirty, ask the user if they want to save.
            #Not implemented.
            shouldClose = True

            if len(MainWindow.mainWindows) == 1 and self.isQuitting is False:
                #This is the last remaining MainWindow open.
                #Transform the current window into a welcome page.
                shouldClose = False
                self.webViewController().clear()
                self.showWelcome()

        else:
            if self._webViewController is not None:
                self._webViewController.cleanup()
            #super(MainWindow, self).closeEvent(event)
            shouldClose = True

        if shouldClose:
            self.webViewController().cleanup()
            MainWindow.mainWindows.remove(self)
            event.accept()
        else:
            event.ignore()

    @Slot()
    def doActionNew(self):
        #Which MainWindow object we create the new worksheet in
        #depends on if doActionNew() is fired on a welcome page
        #or not.
        main_window = None

        if self.isWelcome:
            self.hideWelcome()
            #Use this MainWindow object to create the worksheet.
            main_window = self
        else:
            #Create a new MainWindow object to use for the new worksheet.
            main_window = MainWindow()
            main_window.show()

        #Create a new worksheet
        main_window.webViewController().clear()
        main_window.webViewController().worksheet_controller = WorksheetController.withNewWorksheet(main_window.webViewController())

    @Slot()
    def doActionOpen(self):
        #Ideally, we should check if the current MainWindow is showing a new, clean worksheet,
        #and if so, just delete the empty worksheet and replace it with the newly opened on.
        #We ignore that for now.

        filename = QFileDialog.getOpenFileName(self, "Open Worksheet", filter="Sage Worksheets (*.sws *.txt *.html)")[0]

        if not filename:
            #User clicked cancel.
            return

        #Which MainWindow object we create the new worksheet in
        #depends on if doActionOpen() is fired on a welcome page
        #or not.
        main_window = None

        if self.isWelcome:
            self.hideWelcome()
            #Use this MainWindow object to create the worksheet.
            main_window = self
        else:
            #Create a new MainWindow object to use for the new worksheet.
            main_window = MainWindow()
            main_window.show()

        #Open the worksheet.
        main_window.webViewController().clear()
        main_window.webViewController().worksheet_controller = WorksheetController.withWorksheetFile(main_window.webViewController(), filename)

        #Set the working filename for this MainWindow instance.
        self.filename = filename

    def doActionSave(self):
        if self.filename:
            self.saveFile(self.filename)
        else:
            self.doActionSaveAs()

    def doActionSaveAs(self):
        #getSaveFileName([parent=None[, caption=""[, dir=""[, filter=""[, selectedFilter=""[, options=0]]]]]])
        filename = QFileDialog.getSaveFileName(self, "Save Worksheet",
                                               filter="Sage Worksheet (*.sws);;All files (*)",
                                               selectedFilter="Sage Worksheets (*.sws)")[0]
        if not filename:
            #The user clicked cancel.
            return

        #Make sure the file extension is in the filename.
        if not filename.endswith(".sws"):
            filename += ".sws"

        self.saveFile(filename)

    def saveFile(self, filename):
        #Write out the worksheet to filename whether it exists or not.
        if os.path.exists(filename):
            os.remove(filename)

        #Save the file.
        self.webViewController().worksheet_controller.saveWorksheet(filename)

        #Set the working filename for this MainWindow instance.
        self.filename = filename

    def doActionPrint(self):
        pass

    def doActionQuit(self):
        self.isQuitting = True

    def doActionCopy(self):
        pass

    def doActionCut(self):
        pass

    def doActionPaste(self):
        pass

    def doActionWorksheetProperties(self):
        self.showConsoles()

    def doActionEvaluateWorksheet(self):
        pass

    def doActionInterrupt(self):
        pass

    def doActionAbout(self):
        message_text = """
<b>Guru</b> version 0.nothing (or possibly negative)
<p>Copyright &copy; 2013 Robert Jacobson.</p>
<p>This software makes use of code from the Sage Project (sagemath.org). This software and Sage are both licensed under the GPL v.2.</p>
<p>Guru is running in the following environment.<br>
&nbsp;&nbsp;&nbsp;&nbsp;Python %s<br>
&nbsp;&nbsp;&nbsp;&nbsp;Qt %s<br>
&nbsp;&nbsp;&nbsp;&nbsp;PySide %s<br>
&nbsp;&nbsp;&nbsp;&nbsp;%s (OS)<br>
        """ % (platform.python_version(), QT_VERSION_STR, PYSIDE_VERSION_STR, platform.system())
        QMessageBox.about(self, "About Guru", message_text)

    def doActionSageServer(self):
        pass

