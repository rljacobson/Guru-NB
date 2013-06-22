import platform
import os

from PySide.QtGui import (QMainWindow, QMessageBox, QFileDialog, QAction)
from PySide.QtCore import (SIGNAL, SLOT, Slot, Qt)
#The next two are imported as their PyQt names.
from PySide import __version__ as PYSIDE_VERSION_STR
from PySide.QtCore import __version__ as QT_VERSION_STR

from guru.Ui_MainWindow import Ui_MainWindow
from guru.WebViewController import WebViewController
from guru.WorksheetController import WorksheetController
from guru.Consoles import Consoles
from guru.globals import GURU_ROOT


def isAlive(qobj):
    # #If this object has been completely destroyed, returns False.
    # import sip
    # try:
    #     sip.unwrapinstance(qobj)
    # except RuntimeError:
    #     return False
    # return True
    return True #Unfortunately, the above doesn't work in PySide.

class MainWindow(QMainWindow, Ui_MainWindow):

    #Keep track of the MainWindow objects.
    instances = list()
    #NextID provides numbers to append to new documents: "Untitled-1.sws", "Untitled-2.sws", etc.
    NextID = 0
    #When the user closes the last document window, we transform the window into a Welcome window.
    #On the other hand, if the user selects Quit, we just close the window. We use the isQuitting
    #variable to distinguish between these two cases.
    isQuitting = False
    
    def __init__(self, parent=None, isWelcome=False, file_name=None, isNewFile=False):
        super(MainWindow, self).__init__(parent)

        #Add self to the set of open instances.
        MainWindow.instances.append(self)

        #We want to reclaim the resources of this window when it is closed.
        self.setAttribute(Qt.WA_DeleteOnClose)
        #self.connect(self, SIGNAL("destroyed(QObject*)"), MainWindow.updateInstances)

        #Consoles are just windows displaying logs of various things going on.
        self.consoles_window = Consoles(self) #Hidden until shown.

        #Lazy instantiation. Seems unnecessary at this point, to be honest.
        self._webViewController = None

        #Determines if this is a welcome page window.
        self.isWelcome = isWelcome

        #titleName is the filename without the path. We need a separate entity for titleName
        #because new worksheets do not have a true filename--they aren't files yet.
        self.titleName = None

        self.setupUi()

        if isNewFile:
            self.loadNewFile()

        #This window may be editing a worksheet associated to a file.
        self.file_name = file_name
        if self.file_name is not None:
            self.isWelcome = True #Tricks loadFile into loading the file in the current window.
            self.loadFile(file_name)
    
    def setupUi(self):
        #The superclass sets up most of the UI.
        super(MainWindow, self).setupUi(self)

        #self.setUnifiedTitleAndToolBarOnMac(True)

        self.setCentralWidget(self.webViewController().webView())
        #self.__index = 0

        #Connect all the actions.
        #File actions
        self.connect(self.actionNew, SIGNAL("triggered()"), self.doActionNew)
        self.connect(self.actionOpen, SIGNAL("triggered()"), self.doActionOpen)
        self.connect(self.actionSave, SIGNAL("triggered()"), self.doActionSave)
        self.connect(self.actionSaveAs, SIGNAL("triggered()"), self.doActionSaveAs)
        self.connect(self.actionSaveAll, SIGNAL("triggered()"), self.doActionSaveAll)
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

    def showWelcome(self):
        #Make the UI changes necessary for showing the welcome page.

        #This method is only called if we're a welcome page, so...
        self.isWelcome = True
        self.file_name = None
        self.titleName = None
        self.setWindowTitle("Guru")
        self.updateWindowMenu()

        #Hide the toolbar.
        self.toolBar.hide()

        #Disable the relevant actions.
        self.enableEditingActions(False)

        #Display the welcome page.
        self.webViewController().showHtmlFile("guru_welcome.html")

        #Hook up the javscript bridge.
        #self.webViewController().webView().page().mainFrame().addToJavaScriptWindowObject("GuruWelcome", self)

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

        if not self.isWelcome:
            #If the worksheet is dirty, ask the user if they want to save.
            #Not implemented.
            shouldClose = True

            if len(MainWindow.instances) == 1 and MainWindow.isQuitting is False:
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
            MainWindow.instances.remove(self)
            #We update the Window menu of each open window.
            self.updateWindowMenu()
            event.accept()
        else:
            #The close was cancelled.
            MainWindow.isQuitting = False
            event.ignore()

    def updateWindowMenu(self):
        #aboutToShow() does not do what Mark Summerfield thinks it does--at least in PySide.

        #Generate a list of actions to add to the Window menu.
        window_menu_actions = []
        for i in range(len(MainWindow.instances)):
            window = MainWindow.instances[i]
            action_text = "%d. %s" % (i, window.titleName)
            window_menu_actions.append(QAction(action_text, self, triggered=self.raiseWindow))

        for window in MainWindow.instances:
            window.menu_Window.clear()
            for new_action in window_menu_actions:
                window.menu_Window.addAction(new_action)

    def raiseWindow(self):
        action = self.sender()
        if not isinstance(action, QAction):
            return
        title_text = action.text()
        title_text = title_text[title_text.index('.')+2:] #Peels off the initial numbering, i.e. "2. Untitled.sws".
        for window in MainWindow.instances:
            if window.titleName == title_text:
                window.activateWindow()
                window.raise_()
                break

    def setUniqueWindowTitle(self):
        #This method does the following:
        #   1. gets the filename of the working file, or sets it to Untitled.sws;
        #   2. determines if there are already titleNames with that filename, and if so, how many;
        #   3. using (1) and (2), creates a unique titleName of the form "filename.sws (n)";
        #   4. sets the window title appropriately;
        #   5. calls updateWindowMenu().

        #1. gets the filename of the working file, or sets it to Untitled.sws;
        if self.file_name is not None:
            title_text = os.path.split(self.file_name)[1]
        else:
            title_text = "Untitled.sws"

        #2. determines if there are already titleNames with that filename, and if so, how many;
        existing_titles = [window.titleName for window in MainWindow.instances if window is not self]
        if existing_titles.count(title_text) > 0:
            counter = 1
            while existing_titles.count(title_text + " (%d)"%counter) > 0:
                counter += 1
            #3. using (1) and (2), creates a unique titleName of the form "filename.sws (n)";
            title_text += " (%d)"%counter

        #4. sets the window title appropriately;
        self.setWindowTitle("Guru - %s" % title_text)
        self.titleName = title_text

        #5. calls updateWindowMenu().
        self.updateWindowMenu()

    ############### Actions ###############

    @Slot()
    def doActionNew(self):
        #Which MainWindow object we create the new worksheet in
        #depends on if doActionNew() is fired on a welcome page
        #or not.
        main_window = None

        if self.isWelcome:
            self.hideWelcome()
            self.loadNewFile()
        else:
            #Create a new MainWindow object to use for the new worksheet.
            main_window = MainWindow(isNewFile=True)
            main_window.show()

    def loadNewFile(self):
        #Create a new worksheet
        self.webViewController().newWorksheetFile()

        #Set the title appropriately.
        self.file_name = None
        self.setUniqueWindowTitle()


    @Slot()
    def doActionOpen(self):
        file_name = QFileDialog.getOpenFileName(self, "Open Worksheet", filter="Sage Worksheets (*.sws *.txt *.html)")[0]

        if not file_name:
            #User clicked cancel.
            return

        #Check if the file is already opened. If it is, just raise that window.
        window_list = [window for window in MainWindow.instances if window.file_name == file_name]
        if len(window_list)==0:
            #The file is not open, so open it.
            self.loadFile(file_name)
        else:
            #The file is already open. Just raise its window.
            window_list[0].activateWindow()
            window_list[0].raise_()

    def loadFile(self, file_name):
        #Which MainWindow object we create the new worksheet in depends on if loadFile()
        #is fired on a welcome page or not.

        if self.isWelcome:
            #Use the current MainWindow object to create the worksheet.
            self.hideWelcome()
            #Set the working filename
            self.file_name = file_name
            #We set the window title.
            self.setUniqueWindowTitle()
            #Open the worksheet in the webView.
            self.webViewController().openWorksheetFile(file_name)
        else:
            #Create a new MainWindow object to use for the new worksheet.
            main_window = MainWindow(file_name=file_name)
            main_window.show()

            main_window.activateWindow()
            main_window.raise_()

    def doActionSave(self):
        if self.file_name:
            self.saveFile(self.file_name)
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

    def doActionSaveAll(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def saveFile(self, file_name):
        #Save the file, overwriting any existing file.
        self.webViewController().saveWorksheetFile(file_name)

        #Set the working filename for this MainWindow instance.
        self.file_name = file_name
        self.titleName = os.path.split(file_name)[1]
        self.setUniqueWindowTitle("Guru - " + self.titleName)

    def doActionPrint(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def doActionQuit(self):
        MainWindow.isQuitting = True

        while MainWindow.instances:
            window = MainWindow.instances[0]
            if not window.close():
                break

    def doActionCopy(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def doActionCut(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def doActionPaste(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def doActionWorksheetProperties(self):
        self.showConsoles()

    def doActionEvaluateWorksheet(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def doActionInterrupt(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def doActionAbout(self):
        f = open(os.path.join(GURU_ROOT, 'guru', 'guru_about.html'))

        file_contents = f.read()

        message_text = file_contents % (platform.python_version(), QT_VERSION_STR, PYSIDE_VERSION_STR, platform.system())
        QMessageBox.about(self, "About Guru", message_text)

    def doActionSageServer(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")


