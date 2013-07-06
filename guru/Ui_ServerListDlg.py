# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'guru/Ui_ServerListDlg.ui'
#
# Created: Wed Jul  3 20:44:45 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_ServerListDlg(object):
    def setupUi(self, ServerListDlg):
        ServerListDlg.setObjectName("ServerListDlg")
        ServerListDlg.resize(626, 340)
        self.verticalLayout = QtGui.QVBoxLayout(ServerListDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(ServerListDlg)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.AddServerBtn = QtGui.QToolButton(ServerListDlg)
        self.AddServerBtn.setObjectName("AddServerBtn")
        self.gridLayout.addWidget(self.AddServerBtn, 2, 0, 1, 1)
        self.DeleteServerBtn = QtGui.QToolButton(ServerListDlg)
        self.DeleteServerBtn.setObjectName("DeleteServerBtn")
        self.gridLayout.addWidget(self.DeleteServerBtn, 2, 1, 1, 1)
        self.ServerListView = QtGui.QListWidget(ServerListDlg)
        self.ServerListView.setObjectName("ServerListView")
        self.gridLayout.addWidget(self.ServerListView, 1, 0, 1, 4)
        self.EditBtn = QtGui.QToolButton(ServerListDlg)
        self.EditBtn.setObjectName("EditBtn")
        self.gridLayout.addWidget(self.EditBtn, 2, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.label_2 = QtGui.QLabel(ServerListDlg)
        self.label_2.setTextFormat(QtCore.Qt.AutoText)
        self.label_2.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.buttonBox = QtGui.QDialogButtonBox(ServerListDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(ServerListDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), ServerListDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), ServerListDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(ServerListDlg)

    def retranslateUi(self, ServerListDlg):
        ServerListDlg.setWindowTitle(QtGui.QApplication.translate("ServerListDlg", "Sage Servers", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("ServerListDlg", "Available Sage Servers", None, QtGui.QApplication.UnicodeUTF8))
        self.AddServerBtn.setToolTip(QtGui.QApplication.translate("ServerListDlg", "Add a server", None, QtGui.QApplication.UnicodeUTF8))
        self.AddServerBtn.setText(QtGui.QApplication.translate("ServerListDlg", "+", None, QtGui.QApplication.UnicodeUTF8))
        self.DeleteServerBtn.setToolTip(QtGui.QApplication.translate("ServerListDlg", "Delete server from the list", None, QtGui.QApplication.UnicodeUTF8))
        self.DeleteServerBtn.setText(QtGui.QApplication.translate("ServerListDlg", "-", None, QtGui.QApplication.UnicodeUTF8))
        self.EditBtn.setToolTip(QtGui.QApplication.translate("ServerListDlg", "Edit server configuration", None, QtGui.QApplication.UnicodeUTF8))
        self.EditBtn.setText(QtGui.QApplication.translate("ServerListDlg", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("ServerListDlg", "Guru needs a Sage server to run Sage processes that evaluate cells. Right now, a \"Sage server\" is just a local Sage installation.", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc
