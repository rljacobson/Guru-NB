# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'guru/Ui_EditSageServerDlg.ui'
#
# Created: Fri Jul  5 13:14:36 2013
#      by: pyside-uic 0.2.13 running on PySide 1.1.1
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_EditSageServerDlg(object):
    def setupUi(self, EditSageServerDlg):
        EditSageServerDlg.setObjectName("EditSageServerDlg")
        EditSageServerDlg.resize(602, 188)
        self.verticalLayout = QtGui.QVBoxLayout(EditSageServerDlg)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtGui.QLabel(EditSageServerDlg)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtGui.QLabel(EditSageServerDlg)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTop|QtCore.Qt.AlignTrailing)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 4, 0, 1, 1)
        self.lblDetectedVersion = QtGui.QLabel(EditSageServerDlg)
        self.lblDetectedVersion.setText("")
        self.lblDetectedVersion.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignTop)
        self.lblDetectedVersion.setObjectName("lblDetectedVersion")
        self.gridLayout.addWidget(self.lblDetectedVersion, 4, 1, 1, 1)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.txtPath = QtGui.QLineEdit(EditSageServerDlg)
        self.txtPath.setObjectName("txtPath")
        self.horizontalLayout.addWidget(self.txtPath)
        self.btnOpenPath = QtGui.QToolButton(EditSageServerDlg)
        self.btnOpenPath.setObjectName("btnOpenPath")
        self.horizontalLayout.addWidget(self.btnOpenPath)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        self.label_2 = QtGui.QLabel(EditSageServerDlg)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.txtName = QtGui.QLineEdit(EditSageServerDlg)
        self.txtName.setObjectName("txtName")
        self.gridLayout.addWidget(self.txtName, 0, 1, 1, 1)
        self.label_4 = QtGui.QLabel(EditSageServerDlg)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 5, 0, 1, 1)
        self.DefaultCheckBox = QtGui.QCheckBox(EditSageServerDlg)
        self.DefaultCheckBox.setText("")
        self.DefaultCheckBox.setObjectName("DefaultCheckBox")
        self.gridLayout.addWidget(self.DefaultCheckBox, 5, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtGui.QDialogButtonBox(EditSageServerDlg)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.label.setBuddy(self.txtName)
        self.label_2.setBuddy(self.txtPath)

        self.retranslateUi(EditSageServerDlg)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("accepted()"), EditSageServerDlg.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("rejected()"), EditSageServerDlg.reject)
        QtCore.QMetaObject.connectSlotsByName(EditSageServerDlg)
        EditSageServerDlg.setTabOrder(self.txtName, self.txtPath)
        EditSageServerDlg.setTabOrder(self.txtPath, self.btnOpenPath)
        EditSageServerDlg.setTabOrder(self.btnOpenPath, self.buttonBox)

    def retranslateUi(self, EditSageServerDlg):
        EditSageServerDlg.setWindowTitle(QtGui.QApplication.translate("EditSageServerDlg", "Add Sage Server", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("EditSageServerDlg", "Name for this configuration:", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("EditSageServerDlg", "Detected Sage Version:", None, QtGui.QApplication.UnicodeUTF8))
        self.txtPath.setToolTip(QtGui.QApplication.translate("EditSageServerDlg", "Path to the Sage server", None, QtGui.QApplication.UnicodeUTF8))
        self.btnOpenPath.setText(QtGui.QApplication.translate("EditSageServerDlg", "...", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("EditSageServerDlg", "Path to sage:", None, QtGui.QApplication.UnicodeUTF8))
        self.txtName.setToolTip(QtGui.QApplication.translate("EditSageServerDlg", "Name of the Sage server", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("EditSageServerDlg", "Use this as the default server:", None, QtGui.QApplication.UnicodeUTF8))

