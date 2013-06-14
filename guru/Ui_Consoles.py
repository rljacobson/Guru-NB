# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'guru/Ui_Consoles.ui'
#
# Created: Tue Jun 11 11:36:39 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Consoles(object):
    def setupUi(self, Consoles):
        Consoles.setObjectName("Consoles")
        Consoles.resize(628, 639)
        self.horizontalLayout_2 = QtGui.QHBoxLayout(Consoles)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setSizeConstraint(QtGui.QLayout.SetDefaultConstraint)
        self.verticalLayout.setObjectName("verticalLayout")
        self.tabWidget = QtGui.QTabWidget(Consoles)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtGui.QWidget()
        self.tab.setObjectName("tab")
        self.horizontalLayout_3 = QtGui.QHBoxLayout(self.tab)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.ajax_console = QtGui.QTextBrowser(self.tab)
        self.ajax_console.setObjectName("ajax_console")
        self.horizontalLayout_3.addWidget(self.ajax_console)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtGui.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.horizontalLayout_4 = QtGui.QHBoxLayout(self.tab_2)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.sage_console = QtGui.QTextBrowser(self.tab_2)
        self.sage_console.setObjectName("sage_console")
        self.horizontalLayout_4.addWidget(self.sage_console)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QtGui.QWidget()
        self.tab_3.setObjectName("tab_3")
        self.horizontalLayout_5 = QtGui.QHBoxLayout(self.tab_3)
        self.horizontalLayout_5.setObjectName("horizontalLayout_5")
        self.textBrowser_3 = QtGui.QTextBrowser(self.tab_3)
        self.textBrowser_3.setObjectName("textBrowser_3")
        self.horizontalLayout_5.addWidget(self.textBrowser_3)
        self.tabWidget.addTab(self.tab_3, "")
        self.verticalLayout.addWidget(self.tabWidget)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.closeButton = QtGui.QPushButton(Consoles)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.horizontalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Consoles)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QObject.connect(self.closeButton, QtCore.SIGNAL("clicked()"), Consoles.close)
        QtCore.QMetaObject.connectSlotsByName(Consoles)

    def retranslateUi(self, Consoles):
        Consoles.setWindowTitle(QtGui.QApplication.translate("Consoles", "Consoles", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), QtGui.QApplication.translate("Consoles", "AJAX Communication", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), QtGui.QApplication.translate("Consoles", "Sage Process", None, QtGui.QApplication.UnicodeUTF8))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), QtGui.QApplication.translate("Consoles", "Page", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("Consoles", "Close", None, QtGui.QApplication.UnicodeUTF8))

