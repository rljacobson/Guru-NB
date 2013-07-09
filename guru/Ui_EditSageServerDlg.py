# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'guru/Ui_EditSageServerDlg.ui'
#
# Created: Mon Jul  8 17:12:20 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_EditSageServerDlg(object):
    def setupUi(self, EditSageServerDlg):
        EditSageServerDlg.setObjectName("EditSageServerDlg")
        EditSageServerDlg.resize(663, 422)
        self.verticalLayout_2 = QtGui.QVBoxLayout(EditSageServerDlg)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtGui.QLabel(EditSageServerDlg)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.txtName = QtGui.QLineEdit(EditSageServerDlg)
        self.txtName.setObjectName("txtName")
        self.horizontalLayout_2.addWidget(self.txtName)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.ServerTypeTabs = QtGui.QTabWidget(EditSageServerDlg)
        self.ServerTypeTabs.setTabShape(QtGui.QTabWidget.Rounded)
        self.ServerTypeTabs.setObjectName("ServerTypeTabs")
        self.LocalServerTab = QtGui.QWidget()
        self.LocalServerTab.setObjectName("LocalServerTab")
        self.verticalLayout = QtGui.QVBoxLayout(self.LocalServerTab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_3 = QtGui.QLabel(self.LocalServerTab)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 3, 0, 1, 1)
        self.lblDetectedVersion = QtGui.QLabel(self.LocalServerTab)
        self.lblDetectedVersion.setText("")
        self.lblDetectedVersion.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblDetectedVersion.setObjectName("lblDetectedVersion")
        self.gridLayout.addWidget(self.lblDetectedVersion, 3, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.txtPath = QtGui.QLineEdit(self.LocalServerTab)
        self.txtPath.setObjectName("txtPath")
        self.horizontalLayout.addWidget(self.txtPath)
        self.btnOpenPath = QtGui.QToolButton(self.LocalServerTab)
        self.btnOpenPath.setObjectName("btnOpenPath")
        self.horizontalLayout.addWidget(self.btnOpenPath)
        self.gridLayout.addLayout(self.horizontalLayout, 1, 1, 1, 1)
        self.label_2 = QtGui.QLabel(self.LocalServerTab)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 1, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(20, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 4, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.ServerTypeTabs.addTab(self.LocalServerTab, "")
        self.NotbookServerTab = QtGui.QWidget()
        self.NotbookServerTab.setObjectName("NotbookServerTab")
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.NotbookServerTab)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_4 = QtGui.QLabel(self.NotbookServerTab)
        self.label_4.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 0, 0, 1, 1)
        self.txtNotebookServerURL = QtGui.QLineEdit(self.NotbookServerTab)
        self.txtNotebookServerURL.setObjectName("txtNotebookServerURL")
        self.gridLayout_2.addWidget(self.txtNotebookServerURL, 0, 1, 1, 1)
        self.label_5 = QtGui.QLabel(self.NotbookServerTab)
        self.label_5.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 1, 0, 1, 1)
        self.txtNotebookServerUsername = QtGui.QLineEdit(self.NotbookServerTab)
        self.txtNotebookServerUsername.setObjectName("txtNotebookServerUsername")
        self.gridLayout_2.addWidget(self.txtNotebookServerUsername, 1, 1, 1, 1)
        self.label_6 = QtGui.QLabel(self.NotbookServerTab)
        self.label_6.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 2, 0, 1, 1)
        self.txtNotebookServerPassword = QtGui.QLineEdit(self.NotbookServerTab)
        self.txtNotebookServerPassword.setInputMask("")
        self.txtNotebookServerPassword.setEchoMode(QtGui.QLineEdit.Password)
        self.txtNotebookServerPassword.setObjectName("txtNotebookServerPassword")
        self.gridLayout_2.addWidget(self.txtNotebookServerPassword, 2, 1, 1, 1)
        self.TestLoginBtn = QtGui.QPushButton(self.NotbookServerTab)
        self.TestLoginBtn.setObjectName("TestLoginBtn")
        self.gridLayout_2.addWidget(self.TestLoginBtn, 3, 0, 1, 1)
        self.TestLoginLbl = QtGui.QLabel(self.NotbookServerTab)
        self.TestLoginLbl.setText("")
        self.TestLoginLbl.setWordWrap(True)
        self.TestLoginLbl.setObjectName("TestLoginLbl")
        self.gridLayout_2.addWidget(self.TestLoginLbl, 3, 1, 1, 1)
        self.verticalLayout_3.addLayout(self.gridLayout_2)
        self.label_7 = QtGui.QLabel(self.NotbookServerTab)
        self.label_7.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.label_7.setWordWrap(True)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_3.addWidget(self.label_7)
        self.ServerTypeTabs.addTab(self.NotbookServerTab, "")
        self.verticalLayout_2.addWidget(self.ServerTypeTabs)
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem1 = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem1)
        self.DefaultCheckBox = QtGui.QCheckBox(EditSageServerDlg)
        self.DefaultCheckBox.setObjectName("DefaultCheckBox")
        self.horizontalLayout_3.addWidget(self.DefaultCheckBox)
        self.verticalLayout_2.addLayout(self.horizontalLayout_3)
        self.buttonBox = QtGui.QDialogButtonBox(EditSageServerDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout_2.addWidget(self.buttonBox)
        self.label.setBuddy(self.txtName)
        self.label_2.setBuddy(self.txtPath)
        self.label_4.setBuddy(self.txtNotebookServerURL)
        self.label_5.setBuddy(self.txtNotebookServerUsername)
        self.label_6.setBuddy(self.txtNotebookServerPassword)

        self.retranslateUi(EditSageServerDlg)
        self.ServerTypeTabs.setCurrentIndex(1)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), EditSageServerDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), EditSageServerDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(EditSageServerDlg)
        EditSageServerDlg.setTabOrder(self.txtName, self.ServerTypeTabs)
        EditSageServerDlg.setTabOrder(self.ServerTypeTabs, self.txtPath)
        EditSageServerDlg.setTabOrder(self.txtPath, self.btnOpenPath)
        EditSageServerDlg.setTabOrder(self.btnOpenPath, self.txtNotebookServerURL)
        EditSageServerDlg.setTabOrder(self.txtNotebookServerURL, self.txtNotebookServerUsername)
        EditSageServerDlg.setTabOrder(self.txtNotebookServerUsername, self.txtNotebookServerPassword)
        EditSageServerDlg.setTabOrder(self.txtNotebookServerPassword, self.TestLoginBtn)
        EditSageServerDlg.setTabOrder(self.TestLoginBtn, self.DefaultCheckBox)
        EditSageServerDlg.setTabOrder(self.DefaultCheckBox, self.buttonBox)

    def retranslateUi(self, EditSageServerDlg):
        EditSageServerDlg.setWindowTitle(QtGui.QApplication.translate("EditSageServerDlg", "Add Sage Server", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EditSageServerDlg", "Name for this configuration:", None, QtGui.QApplication.UnicodeUTF8))
        self.txtName.setToolTip(QtGui.QApplication.translate("EditSageServerDlg", "Name of the Sage server", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("EditSageServerDlg", "Detected Sage Version:", None, QtGui.QApplication.UnicodeUTF8))
        self.txtPath.setToolTip(QtGui.QApplication.translate("EditSageServerDlg", "Path to the Sage server", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOpenPath.setText(QtGui.QApplication.translate("EditSageServerDlg", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("EditSageServerDlg", "Path to sage:", None, QtGui.QApplication.UnicodeUTF8))
        self.ServerTypeTabs.setTabText(self.ServerTypeTabs.indexOf(self.LocalServerTab), QtGui.QApplication.translate("EditSageServerDlg", "Local Sage Installation", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("EditSageServerDlg", "URL of the Sage Notebook Server:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_5.setText(QtGui.QApplication.translate("EditSageServerDlg", "Username:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_6.setText(QtGui.QApplication.translate("EditSageServerDlg", "Password:", None, QtGui.QApplication.UnicodeUTF8))
        self.TestLoginBtn.setText(QtGui.QApplication.translate("EditSageServerDlg", "Verify Login", None, QtGui.QApplication.UnicodeUTF8))
        self.label_7.setText(QtGui.QApplication.translate("EditSageServerDlg", "<html><head/><body><p><span style=\" font-weight:600;\">WARNING:</span> The username and password will be stored in plain text on your computer which is a potential security risk.<br/><br/>When using a Sage Notebook Server, Guru will create temporary worksheets on the server with the prefix &quot;Guru - &quot; and a timestamp.</p></body></html>", None, QtGui.QApplication.UnicodeUTF8))
        self.ServerTypeTabs.setTabText(self.ServerTypeTabs.indexOf(self.NotbookServerTab), QtGui.QApplication.translate("EditSageServerDlg", "Sage Notebook Server", None, QtGui.QApplication.UnicodeUTF8))
        self.DefaultCheckBox.setText(QtGui.QApplication.translate("EditSageServerDlg", "Use this as the default server.", None, QtGui.QApplication.UnicodeUTF8))

