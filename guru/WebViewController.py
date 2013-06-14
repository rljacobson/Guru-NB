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


from jinja2 import FileSystemLoader
from jinja2 import Environment as Jinja2Environment
from webassets import Environment as AssetsEnvironment
from webassets.ext.jinja2 import AssetsExtension

#We will eventually drop in a functional version of the following.
from flaskext.babel import gettext

from guru.WorksheetController import WorksheetController

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

        #Lazy instantiation.
        self._webView = None
        self._base_url = None
        self.jinja2_env = None
        self.jinja_context = None

        #Hook up our webView
        self.connect(self.webView().page(), SIGNAL("unsupportedContent(QNetworkReply*)"), self.webPageError)
        self.connect(self.webView(), SIGNAL("statusBarMessage(QString)"), self.updateStatusBar)

        #Set up a WorksheetController
        self.worksheet_controller = None
        #self.worksheet_controller = WorksheetController.withNewWorksheet(self)

        #Display something in the webview.
        #self.show_rendered_template("html/guru_welcome.html")

    def webView(self):
        """
        :return: The QWebView object associated to the controller.
        """
        if self._webView==None:
            self._webView = QWebView()
            #Set up our fake ajax connection.

        return self._webView

    def setBaseUrl(self, url):
        """
        Sets the base URL used by the QWebView object.

        :param url: String containing the path to the Guru/sagenb directory.
        """
        self._base_url = QUrl(url)
        self._base_url.setScheme("file")

    def baseUrl(self):
        """
        Returns the base URL used by the QWebViewObject.

        :return: String containing the path to the Guru/sagenb directory.
        """
        if self._base_url == None:
            #This magic gets the Guru directory.
            tmp = os.path.dirname(sys.argv[0])
            tmp = os.path.abspath(tmp)
            tmp = os.path.join(tmp, "sagenb", "")
            self._base_url = QUrl(tmp)
            self._base_url.setScheme("file")
            self.putAjaxConsole(self._base_url.path())

        return self._base_url

    def show_rendered_template(self, template_name, **args):
        self.webView().page().mainFrame().setHtml(self.render_template(template_name, **args), self.baseUrl())


    def render_template(self, template_name, **args):
        if self.jinja2_env==None:
            #We need to setup the jinja environment.
            assets_env = AssetsEnvironment(os.path.join(self.baseUrl().path(), "data"), "data")
            self.jinja2_env = Jinja2Environment(loader=FileSystemLoader(os.path.join(self.baseUrl().path(), "data", "sage")), extensions=[AssetsExtension])
            self.jinja2_env.assets_environment = assets_env

            #Now set the jinja context.
            self.jinja_context = {'sitename': gettext('Sage Notebook'),
                       'sage_version': 'unknown',
                       'MATHJAX': True,
                       'gettext': gettext,
                       'JEDITABLE_TINYMCE': True,
                       'conf': None}

        args.update(self.jinja_context)
        template = self.jinja2_env.get_template(template_name)

        renderedpage = template.render(args)

        # from random import randint
        # import codecs
        # f = codecs.open("/Users/rljacobson/Downloads/ " + str(randint(1, 100000)) + ".html", mode='w', encoding='utf-8')
        # f.write(renderedpage)
        # f.close()
        return renderedpage

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
        #If I don't do this we segfault because the javascript Bridge tries to reference an
        #invalid pointer once this instance is garbage collected.
        self._webView.setHtml("")

    def clear(self):
        if self.worksheet_controller is not None:
            self.worksheet_controller.cleanup()
            self.worksheet_controller = None