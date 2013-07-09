import platform
import os

from PySide.QtGui import (QMainWindow, QMessageBox, QFileDialog, QAction, QIcon, QPixmap, QApplication)
from PySide.QtCore import (SIGNAL, SLOT, Slot, Qt, QObject, QSettings)
#The next two are imported as their PyQt names.
from PySide import __version__ as PYSIDE_VERSION_STR
from PySide.QtCore import __version__ as QT_VERSION_STR
from PySide.QtWebKit import QWebPage

from guru.Ui_MainWindow import Ui_MainWindow
from guru.WebViewController import WebViewController
from guru.WorksheetController import WorksheetController
from guru.Consoles import Consoles
from guru.globals import GURU_ROOT, GURU_ONLINE_DOCUMENTATION
from guru.ServerConfigurations import ServerConfigurations
from guru.ServerListDlg import ServerListDlg
import guru.resources_rc


# MainWindow.restoreSettings() is called if this is the first window on app startup.
# MainWindow.saveSettings() is called when the last MainWindow of the app closes,
# which means application termination is imminent.

class MainWindow(QMainWindow, Ui_MainWindow):

    #Keep track of the MainWindow objects.
    instances = list()
    #NextID provides numbers to append to new documents: "Untitled-1.sws", "Untitled-2.sws", etc.
    NextID = 0
    #When the user closes the last document window, we transform the window into a Welcome window.
    #On the other hand, if the user selects Quit, we just close the window. We use the isQuitting
    #variable to distinguish between these two cases.
    isQuitting = False

    recentFiles = []

    def __init__(self, parent=None, isWelcome=False, file_name=None, isNewFile=False):
        super(MainWindow, self).__init__(parent)

        #Add self to the set of open instances.
        MainWindow.instances.append(self)

        #We want to reclaim the resources of this window when it is closed.
        self.setAttribute(Qt.WA_DeleteOnClose)

        self.file_name = file_name

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

        if self.isWelcome:
            self.restoreSettings()

        #restoreSettings() has initialized ServerConfigurations (among other things).
        #If no servers are configured, open the ServerListDlg so the user can configure a server.
        if not ServerConfigurations.server_list:
            self.doActionSageServer()

        if isNewFile:
            self.loadNewFile()

        #This window may be editing a worksheet associated to a file.
        if self.file_name is not None:
            self.isWelcome = True #Tricks loadFile into loading the file in the current window.
            self.loadFile(file_name)
    
    def setupUi(self):
        #The superclass sets up most of the UI.
        super(MainWindow, self).setupUi(self)

        #self.setUnifiedTitleAndToolBarOnMac(True)

        webview = self.webViewController().webView()
        self.setCentralWidget(webview)

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
        #These actions are provided by the WebView instance.
        self.actionCopy = webview.pageAction(QWebPage.Copy)
        iconCopy = QIcon()
        iconCopy.addPixmap(QPixmap(":/images/images/copy-item.png"), QIcon.Normal, QIcon.Off)
        self.actionCopy.setIcon(iconCopy)
        self.actionCopy.setObjectName("actionCopy")
        
        self.actionCut = webview.pageAction(QWebPage.Cut)
        iconCut = QIcon()
        iconCut.addPixmap(QPixmap(":/images/images/Scissors.png"), QIcon.Normal, QIcon.Off)
        self.actionCut.setIcon(iconCut)
        self.actionCut.setObjectName("actionCut")
        
        self.actionPaste = webview.pageAction(QWebPage.Paste)
        iconPaste = QIcon()
        iconPaste.addPixmap(QPixmap(":/images/images/paste2_30.png"), QIcon.Normal, QIcon.Off)
        self.actionPaste.setIcon(iconPaste)
        self.actionPaste.setObjectName("actionPaste")

        self.actionUndo = webview.pageAction(QWebPage.Undo)
        self.actionUndo.setObjectName("actionUndo")
        self.actionRedo = webview.pageAction(QWebPage.Redo)
        self.actionRedo.setObjectName("actionRedo")

        self.menuEdit.addAction(self.actionCopy)
        self.menuEdit.addAction(self.actionCut)
        self.menuEdit.addAction(self.actionPaste)
        self.menuEdit.addAction(self.actionUndo)
        self.menuEdit.addAction(self.actionRedo)

        self.toolBar.insertAction(self.actionEvaluateWorksheet, self.actionCopy)
        self.toolBar.insertAction(self.actionEvaluateWorksheet, self.actionCut)
        self.toolBar.insertAction(self.actionEvaluateWorksheet, self.actionPaste)
        self.toolBar.insertSeparator(self.actionEvaluateWorksheet)

        #This is normally done in retranslateUi, but that method has already been called.
        self.retranslateEditMenuUi()

        #Worksheet actions
        self.connect(self.actionWorksheetProperties, SIGNAL("triggered()"), self.doActionWorksheetProperties)
        self.connect(self.actionEvaluateWorksheet, SIGNAL("triggered()"), self.doActionEvaluateWorksheet)
        self.connect(self.actionInterrupt, SIGNAL("triggered()"), self.doActionInterrupt)
        self.connect(self.actionRestartWorksheet, SIGNAL("triggered()"), self.doActionRestartWorksheet)
        self.connect(self.actionHideAllOutput, SIGNAL("triggered()"), self.doActionHideAllOutput)
        self.connect(self.actionShowAllOutput, SIGNAL("triggered()"), self.doActionShowAllOutput)
        self.connect(self.actionDeleteAllOutput, SIGNAL("triggered()"), self.doActionDeleteAllOutput)

        #Miscellaneous actions
        self.connect(self.actionAbout, SIGNAL("triggered()"), self.doActionAbout)
        self.connect(self.actionOnlineDocumentation, SIGNAL("triggered()"), self.doActionOnlineDocumentation)
        self.connect(self.actionSageServer, SIGNAL("triggered()"), self.doActionSageServer)

        if self.isWelcome:
            #Display the welcome screen.
            self.showWelcome()

    def retranslateEditMenuUi(self):
        #This is normally done in retranslateUi, but that method has already been called.
        self.actionCopy.setText(QApplication.translate("MainWindow", "&Copy", None, QApplication.UnicodeUTF8))
        self.actionCopy.setToolTip(QApplication.translate("MainWindow", "Copy", None, QApplication.UnicodeUTF8))
        self.actionCopy.setShortcut(QApplication.translate("MainWindow", "Ctrl+C", None, QApplication.UnicodeUTF8))
        self.actionCut.setText(QApplication.translate("MainWindow", "Cu&t", None, QApplication.UnicodeUTF8))
        self.actionCut.setToolTip(QApplication.translate("MainWindow", "Cut", None, QApplication.UnicodeUTF8))
        self.actionCut.setShortcut(QApplication.translate("MainWindow", "Ctrl+X", None, QApplication.UnicodeUTF8))
        self.actionPaste.setText(QApplication.translate("MainWindow", "&Paste", None, QApplication.UnicodeUTF8))
        self.actionPaste.setToolTip(QApplication.translate("MainWindow", "Paste from clipboard", None, QApplication.UnicodeUTF8))
        self.actionPaste.setShortcut(QApplication.translate("MainWindow", "Ctrl+V", None, QApplication.UnicodeUTF8))
        self.actionUndo.setText(QApplication.translate("MainWindow", "&Undo", None, QApplication.UnicodeUTF8))
        self.actionUndo.setToolTip(QApplication.translate("MainWindow", "Undo last edit", None, QApplication.UnicodeUTF8))
        self.actionUndo.setShortcut(QApplication.translate("MainWindow", "Ctrl+Z", None, QApplication.UnicodeUTF8))
        self.actionRedo.setText(QApplication.translate("MainWindow", "&Redo", None, QApplication.UnicodeUTF8))
        self.actionRedo.setToolTip(QApplication.translate("MainWindow", "Redo last edit", None, QApplication.UnicodeUTF8))
        self.actionRedo.setShortcut(QApplication.translate("MainWindow", "Shift+Ctrl+Z", None, QApplication.UnicodeUTF8))


    def restoreSettings(self):
        settings = QSettings()

        #Restore recent files list.
        MainWindow.recentFiles = settings.value("RecentFiles")
        if MainWindow.recentFiles is None:
            MainWindow.recentFiles = []
        self.updateRecentFilesMenu()

        #Restore window geometry
        self.restoreGeometry(settings.value("MainWindow/Geometry"))
        self.restoreState(settings.value("MainWindow/State"))

        #Populate the list of available Sage servers.
        sage_servers = settings.value("ServerConfigurations")
        if sage_servers is None:
            sage_servers = []
        ServerConfigurations.restoreFromList(sage_servers)


    def saveSettings(self):
        settings = QSettings()
        settings.setValue("RecentFiles", MainWindow.recentFiles)
        settings.setValue("MainWindow/Geometry", self.saveGeometry())
        settings.setValue("MainWindow/State", self.saveState())
        settings.setValue("ServerConfigurations", ServerConfigurations.server_list)

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
            self._welcomeHandler.OpenRecentFunction = self.loadFile

        #Connect the javascript bridge.
        self.connect(self.webViewController().webView().page().mainFrame(), SIGNAL("javaScriptWindowObjectCleared()"), self.addJavascriptBridge)
        #When the welcome page finishes loading, we add the recent files.
        self.connect(self.webViewController().webView(), SIGNAL('loadFinished(bool)'), self.addRecentFilesToWelcomePage);
        #Display the welcome page.
        self.webViewController().showHtmlFile("guru_welcome.html")

    def addRecentFilesToWelcomePage(self):
        #If we are displaying the welcome page, add the recent files to the recent files list.
        if self.isWelcome:
            for recent_file in MainWindow.recentFiles:
                self.webViewController().addToRecentFiles(recent_file)

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
        #Disconnect the recent files update so we don't add them twice the second time around.
        self.disconnect(self.webViewController().webView(), SIGNAL('loadFinished(bool)'), self.addRecentFilesToWelcomePage)

    #The editing actions are only relevant if we are editing a worksheet.
    #Otherwise (i.e. for the welcome page), they should be disabled.
    def enableEditingActions(self, enabling=True):

        #Worksheet Menu
        self.actionInterrupt.setEnabled(enabling)
        self.actionHideAllOutput.setEnabled(enabling)
        self.actionShowAllOutput.setEnabled(enabling)
        self.actionDeleteAllOutput.setEnabled(enabling)
        self.actionEvaluateWorksheet.setEnabled(enabling)
        self.actionInterrupt.setEnabled(enabling)
        self.actionRestartWorksheet.setEnabled(enabling)

        #Edit Menu
        #These are taken care of by the webview itself.
        # self.actionPaste.setEnabled(enabling)
        # self.actionSave.setEnabled(enabling)
        # self.actionCut.setEnabled(enabling)
        # self.actionCopy.setEnabled(enabling)
        # self.actionUndo.setEnabled(enabling)
        # self.actionRedo.setEnabled(enabling)

        #Miscellaneous
        #self.actionSageServer.setEnabled(enabling)
        self.actionWorksheetProperties.setEnabled(enabling)

        #File Menu
        self.actionPrint.setEnabled(enabling)
        self.actionSaveAs.setEnabled(enabling)
        self.actionSaveAll.setEnabled(enabling)


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
            #Is this the last window to close?
            if not MainWindow.instances:
                #This is the last window, so save application settings.
                self.saveSettings()
            else:
                #This is not the last window, so update the Window menu.
                self.updateWindowMenu()
            event.accept()
        else:
            #The close was cancelled.
            MainWindow.isQuitting = False
            event.ignore()

    def updateRecentFilesMenu(self):
        #If there is a current file open, add it to the recent files list.
        if self.file_name and MainWindow.recentFiles.count(self.file_name) == 0:
            #Prepend the file to recentFiles
            MainWindow.recentFiles.insert(0, self.file_name)
            #This this is the only time files get added to recentFiles,
            #enforce the maximum length of recentFiles now.
            while len(MainWindow.recentFiles) > 9:
                MainWindow.recentFiles.pop()

        recent_files = []

        #For each file in recentFiles, check that it exists and is readable.
        for fname in MainWindow.recentFiles:
            if os.access(fname, os.F_OK):
                recent_files.append(fname)

        MainWindow.recentFiles = recent_files

        #Now create an action for each file.
        if recent_files:
            action_list = []
            for i, fname in enumerate(recent_files):
                new_action = QAction("%d. %s"%(i, fname), self, triggered=self.openRecentFile)
                new_action.setData(fname)
                action_list.append(new_action)
            #Now update the recent files menu on every window.
            for window in MainWindow.instances:
                window.menuRecent.clear()
                window.menuRecent.addActions(action_list)

    def openRecentFile(self):
        action = self.sender()
        if not isinstance(action, QAction):
            return
        self.loadFile(action.data())

    def updateWindowMenu(self):
        #aboutToShow() does not do what Mark Summerfield thinks it does--at least in PySide.

        #Generate a list of actions to add to the Window menu.
        window_menu_actions = []
        for i, window in enumerate(MainWindow.instances):
            #The following line removes the "[*]" from the titleName.
            title_name = ''.join(window.titleName.split("[*]"))
            action_text = "%d. %s" % (i, title_name)
            new_action = QAction(action_text, self, triggered=self.raiseWindow)
            new_action.setData(window.titleName)
            window_menu_actions.append(new_action)

        for window in MainWindow.instances:
            window.menuWindow.clear()
            for new_action in window_menu_actions:
                window.menuWindow.addAction(new_action)

    def raiseWindow(self):
        action = self.sender()
        if not isinstance(action, QAction):
            return
        title_name = action.data()
        #title_text = title_text[title_text.index('.')+2:] #Peels off the initial numbering, i.e. "2. Untitled.sws".
        for window in MainWindow.instances:
            if window.titleName == title_name:
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
            self.updateRecentFilesMenu()
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
        if self.file_name:
            suggested_filename = self.file_name
        else:
            suggested_filename = self.webViewController().worksheet_controller.getTitle()
            #Make sure the file extension is in the filename.
            if not suggested_filename.endswith(".sws"):
                suggested_filename += ".sws"

        suggested_filename = os.path.join(os.curdir, suggested_filename)

        #getSaveFileName([parent=None[, caption=""[, dir=""[, filter=""[, selectedFilter=""[, options=0]]]]]])
        filename = QFileDialog.getSaveFileName(self, caption="Save Worksheet",
                                               dir=suggested_filename,
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
        for window in MainWindow.instances:
            window.doActionSave()

    def saveFile(self, file_name):
        #Save the file, overwriting any existing file.
        self.webViewController().saveWorksheetFile(file_name)

        #Set the working filename for this MainWindow instance.
        self.file_name = file_name
        self.setUniqueWindowTitle()

        self.updateRecentFilesMenu()

    def doActionPrint(self):
        QMessageBox.information(self, "Not Implemented", "Not implemented.")

    def doActionQuit(self):
        MainWindow.isQuitting = True

        while MainWindow.instances:
            window = MainWindow.instances[-1]
            if not window.close():
                break

    def doActionWorksheetProperties(self):
        self.showConsoles()

    def doActionEvaluateWorksheet(self):
        self.webViewController().worksheet_controller.evaluateAll()

    def doActionInterrupt(self):
        self.webViewController().worksheet_controller.interrupt()

    def doActionHideAllOutput(self):
        self.webViewController().worksheet_controller.hideAllOutput()

    def doActionShowAllOutput(self):
        self.webViewController().worksheet_controller.showAllOutput()

    def doActionDeleteAllOutput(self):
        self.webViewController().worksheet_controller.deleteAllOutput()

    def doActionRestartWorksheet(self):
        self.webViewController().worksheet_controller.restartWorksheet()

    def doActionTypesetOutput(self):
        pass
        #self.webViewController().worksheet_controller.typesetOutput(True)

    def doActionAbout(self):
        f = open(os.path.join(GURU_ROOT, 'guru', 'guru_about.html'))

        file_contents = f.read()

        message_text = file_contents % (platform.python_version(), QT_VERSION_STR, PYSIDE_VERSION_STR, platform.system())
        QMessageBox.about(self, "About Guru", message_text)

    def doActionOnlineDocumentation(self):
        os.system('open %s 1>&2 > /dev/null &'% GURU_ONLINE_DOCUMENTATION)

    def doActionSageServer(self):
        server_list_dialog = ServerListDlg(self)

        #Get a reference to the WorksheetController associated to this window.
        wsc = self.webViewController().worksheet_controller

        #Select the server associated to this window, if there is one.
        if wsc and wsc.server_configuration:
            server_list_dialog.selectServer(wsc.server_configuration)

        #Show the dialog.
        server_list_dialog.exec_()

        #It's possible that the user will delete all of the servers. It's not clear how to cleanly handle this case.
        #We choose to give the user a choice to fix the situation.
        while not ServerConfigurations.server_list:
            #No servers?
            message_text = "Guru needs a Sage server configured in order to evaluate cells. " \
                            "Add a Sage server configuration in the server configuration dialog?"
            response = QMessageBox.question(self, "Sage Not Configured", message_text, QMessageBox.Yes, QMessageBox.No)
            if response == QMessageBox.No:
                return
            server_list_dialog.exec_()

        #Execution only reaches this point if there exists a server.
        server_name = server_list_dialog.ServerListView.currentItem().text()
        if wsc:
            new_config = ServerConfigurations.getServerByName(server_name)
            wsc.useServerConfiguration(new_config)

#For reasons unknown, adding the parent of a WebView as a JavaScriptWindowObject
#of the WebView results in a segfault when the parent is destroyed. We get around
#this with a dummy class.
class WelcomeHandler(QObject):
    def __init__(self, parent=None):
        super(WelcomeHandler, self).__init__(parent)
        self.NewFunction = None
        self.OpenFunction = None
        self.OpenRecentFunction = None
        self.AddRecentFunction = None

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

    @Slot(str)
    def OpenRecent(self, recent_number):
        if self.OpenRecentFunction is None:
            QMessageBox.information(self, "Not Implemented", "Not implemented.")
        else:
            self.OpenRecentFunction(recent_number)

