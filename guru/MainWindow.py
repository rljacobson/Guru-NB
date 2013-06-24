import platform
import os

from PySide.QtGui import (QMainWindow, QMessageBox, QFileDialog, QAction)
from PySide.QtCore import (SIGNAL, SLOT, Slot, Qt, QObject)
#The next two are imported as their PyQt names.
from PySide import __version__ as PYSIDE_VERSION_STR
from PySide.QtCore import __version__ as QT_VERSION_STR

from guru.Ui_MainWindow import Ui_MainWindow
from guru.WebViewController import WebViewController
from guru.WorksheetController import WorksheetController
from guru.Consoles import Consoles
from guru.globals import GURU_ROOT

#For reasons unknown, adding the parent of a WebView as a JavaScriptWindowObject
#of the WebView results in a segfault when the parent is destroyed. We get around
#this with a dummy class.
class WelcomeHandler(QObject):
    def __init__(self, parent=None):
        super(WelcomeHandler, self).__init__(parent)
        self.NewFunction = None
        self.OpenFunction = None
        self.RecentFunction = None

    @Slot()
    def New(self):
        if self.NewFunction is None:
            QMessageBox.information(self, "Not Implemented", "Not implemented.")
        else:
            self.NewFunction()

    @Slot()
    def Open(self):
        if self.OpenFunction is None:
            QMessageBox.information(self, "Not Implemented", "Not implemented.")
        else:
            self.OpenFunction()

    @Slot(int)
    def Recent(self, recent_number):
        if self.RecentFunction is None:
            QMessageBox.information(self, "Not Implemented", "Not implemented.")
        else:
            self.RecentFunction(recent_number)



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

        #Consoles are just windows displaying logs of various things going on.
        self.consoles_window = Consoles(self) #Hidden until shown.

        #Lazy instantiation. Seems unnecessary at this point, to be honest.
        self._webViewController = None

        #See the WelcomeHandler class for more information.
        self._welcomeHandler = None

        #Determines if this is a welcome page window.
        self.isWelcome = isWelcome

        #titleName is the filename without the path. We need a separate entity for titleName
        #because new worksheets do not have a true filename--they aren't files yet.
        self.titleName = None

        self.isDirty = False

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
        #Why am I using lazy instantiation here? We'll leave it like this for now.
        if self._webViewController is None:
            self._webViewController = WebViewController(putAjaxConsole = self.consoles_window.putAjaxMessage, putSageConsole = self.consoles_window.putSageProcessMessage)
            #self._webViewController = WebViewController(putAjaxConsole = self.simpleConsole, putSageConsole = self.simpleConsole)

        return self._webViewController

    def showWelcome(self):
        #Make the UI changes necessary for showing the welcome page.

        #This method is only called if we're a welcome page, so...
        self.isWelcome = True
        self.file_name = None
        self.titleName = "Welcome"
        self.setWindowTitle("Guru")
        self.dirty(False)
        self.updateWindowMenu()

        #Hide the toolbar.
        self.toolBar.hide()

        #Disable the relevant actions.
        self.enableEditingActions(False)

        #Hook up the javscript bridge.
        if self._welcomeHandler is None:
            self._welcomeHandler = WelcomeHandler(self)
            self._welcomeHandler.NewFunction = self.doActionNew
            self._welcomeHandler.OpenFunction = self.doActionOpen
        self.connect(self.webViewController().webView().page().mainFrame(), SIGNAL("javaScriptWindowObjectCleared()"), self.addJavascriptBridge)

        #Display the welcome page.
        self.webViewController().showHtmlFile("guru_welcome.html")


    def addJavascriptBridge(self):
        #This method is called whenever new content is loaded into the webFrame.
        #Each time this happens, we need to reconnect the Python-javascript bridge.
        self.webViewController().webView().page().mainFrame().addToJavaScriptWindowObject("GuruWelcome", self._welcomeHandler)

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
        shouldClose = True

        if not self.isWelcome:
            if self.isDirty:
                #If the worksheet is dirty, ask the user if they want to save.
                response = QMessageBox.question(self, "Guru - Unsaved Changes",
                                                "You have unsaved changes. Close anyway?",
                                                QMessageBox.Ok|QMessageBox.Cancel)
                if response == QMessageBox.Ok:
                    shouldClose = True
                else:
                    shouldClose = False

            if len(MainWindow.instances) == 1 and MainWindow.isQuitting is False and shouldClose is True:
                #This is the last remaining MainWindow open.
                #Transform the current window into a welcome page.
                shouldClose = False
                self.webViewController().clear()
                self.showWelcome()

        else:
            shouldClose = True

        if shouldClose:
            if self._webViewController:
                self._webViewController.cleanup()

            MainWindow.instances.remove(self)
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
            title_text = os.path.basename(self.file_name)
        else:
            title_text = "Untitled.sws"

        title_text += "[*]" #Dirty flag.

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

    #@Slot(bool)
    def dirty(self, isDirty):
        self.isDirty = isDirty
        self.setWindowModified(isDirty)

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
        self.dirty(False)
        self.connect(self.webViewController().worksheet_controller, SIGNAL("dirty(bool)"), self.dirty)

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
            #Set the dirty flag handler.
            self.dirty(False)
            self.connect(self.webViewController().worksheet_controller, SIGNAL("dirty(bool)"), self.dirty)
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
        self.setUniqueWindowTitle()

    def doActionPrint(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def doActionQuit(self):
        MainWindow.isQuitting = True

        while MainWindow.instances:
            window = MainWindow.instances[-1]
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


