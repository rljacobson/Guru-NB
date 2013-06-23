import os, sys

from PySide.QtCore import (QObject, QUrl, SIGNAL)
from PySide.QtWebKit import (QWebView, QWebSettings)

#Turn on javascript console.
QWebSettings.globalSettings().setAttribute(QWebSettings.DeveloperExtrasEnabled, True)
#Relax default security settings.
QWebSettings.globalSettings().setAttribute(QWebSettings.LocalContentCanAccessRemoteUrls, True)
QWebSettings.globalSettings().setAttribute(QWebSettings.LocalContentCanAccessFileUrls, True)
QWebSettings.globalSettings().setAttribute(QWebSettings.LocalStorageEnabled, True)
QWebSettings.globalSettings().setAttribute(QWebSettings.OfflineStorageDatabaseEnabled, True)
QWebSettings.globalSettings().setAttribute(QWebSettings.OfflineWebApplicationCacheEnabled, True)

from guru.WorksheetController import WorksheetController
from guru.globals import GURU_ROOT

class WebViewController(QObject):

    def __init__(self, statusBar=None, putAjaxConsole=None, putSageConsole=None):
        super(WebViewController, self).__init__()

        #These typically are hooked up to UI elements.
        self.statusBar = statusBar
        if putAjaxConsole is None:
            self.putAjaxConsole = self.dummyConsole
        else:
            self.putAjaxConsole = putAjaxConsole
        if putSageConsole is None:
            self.putSageConsole = self.dummyConsole
        else:
            self.putSageConsole = putSageConsole

        self._webView = None #Lazy instantiation.

        #Set up a WorksheetController
        self.worksheet_controller = None

    def webView(self):
        """
        :return: The QWebView object associated to the controller.
        """
        if self._webView is None:
            self._webView = QWebView()
            #Hook up our webView to UI, log, etc.
        self.connect(self._webView.page(), SIGNAL("unsupportedContent(QNetworkReply*)"), self.webPageError)
        self.connect(self._webView, SIGNAL("statusBarMessage(QString)"), self.updateStatusBar)

        return self._webView

    def showHtmlFile(self, file_name):
        url = QUrl(os.path.join(GURU_ROOT, 'guru', file_name))
        url.setScheme("file")
        #What is the difference between load() and setUrl()?
        self.webView().page().mainFrame().load(url)

    def openWorksheetFile(self, file_name):
        self.clear()
        self.worksheet_controller = WorksheetController.withWorksheetFile(self, file_name)

    def saveWorksheetFile(self, file_name):
        #Save the file, overwriting any existing file.
        self.worksheet_controller.saveWorksheet(file_name)

    def newWorksheetFile(self):
        #Create a new worksheet.
        self.clear()
        self.worksheet_controller = WorksheetController.withNewWorksheet(self)

    def webPageError(self, reply):
        print "Web page error: %s" % reply.error()

    def updateStatusBar(self, text):
        if self.statusBar == None:
            #print "Status bar text: %s" % text
            pass

    def dummyConsole(self, text):
        #Do nothing.
        pass

    def cleanup(self):
        if self.worksheet_controller:
            self.worksheet_controller.cleanup()
        self.worksheet_controller = None

    def clear(self):
        if self.worksheet_controller is not None:
            self.worksheet_controller.cleanup()
            self.worksheet_controller = None