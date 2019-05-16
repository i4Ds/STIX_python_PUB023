# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mongodb.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(772, 483)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.label_4 = QtWidgets.QLabel(Dialog)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 1, 2, 1, 2)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 1, 5, 1, 1)
        self.treeWidget = QtWidgets.QTreeWidget(Dialog)
        self.treeWidget.setObjectName("treeWidget")
        self.treeWidget.header().setDefaultSectionSize(150)
        self.treeWidget.header().setHighlightSections(False)
        self.gridLayout.addWidget(self.treeWidget, 2, 0, 1, 6)
        self.pwdLineEdit = QtWidgets.QLineEdit(Dialog)
        self.pwdLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pwdLineEdit.setObjectName("pwdLineEdit")
        self.gridLayout.addWidget(self.pwdLineEdit, 1, 4, 1, 1)
        self.portLineEdit = QtWidgets.QLineEdit(Dialog)
        self.portLineEdit.setObjectName("portLineEdit")
        self.gridLayout.addWidget(self.portLineEdit, 0, 4, 1, 1)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.gridLayout.addWidget(self.label_3, 1, 0, 1, 1)
        self.serverLineEdit = QtWidgets.QLineEdit(Dialog)
        self.serverLineEdit.setObjectName("serverLineEdit")
        self.gridLayout.addWidget(self.serverLineEdit, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(208, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 5, 1, 1)
        self.userLineEdit = QtWidgets.QLineEdit(Dialog)
        self.userLineEdit.setObjectName("userLineEdit")
        self.gridLayout.addWidget(self.userLineEdit, 1, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 5, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.statusLabel = QtWidgets.QLabel(Dialog)
        self.statusLabel.setText("")
        self.statusLabel.setObjectName("statusLabel")
        self.gridLayout.addWidget(self.statusLabel, 3, 0, 1, 5)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.label_2.setText(_translate("Dialog", "Port"))
        self.label_4.setText(_translate("Dialog", "Password"))
        self.pushButton.setText(_translate("Dialog", "Connect"))
        self.treeWidget.headerItem().setText(0, _translate("Dialog", "ID"))
        self.treeWidget.headerItem().setText(1, _translate("Dialog", "Filename"))
        self.treeWidget.headerItem().setText(2, _translate("Dialog", "Creation time"))
        self.treeWidget.headerItem().setText(3, _translate("Dialog", "Start"))
        self.treeWidget.headerItem().setText(4, _translate("Dialog", "End"))
        self.portLineEdit.setText(_translate("Dialog", "27017"))
        self.label_3.setText(_translate("Dialog", "Username"))
        self.serverLineEdit.setText(_translate("Dialog", "localhost"))
        self.label.setText(_translate("Dialog", "Server"))


