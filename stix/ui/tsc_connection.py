# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'tsc_connection.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(477, 78)
        self.gridLayout = QtWidgets.QGridLayout(Dialog)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel
                                          | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 2, 4, 1, 1)
        self.serverLineEdit = QtWidgets.QLineEdit(Dialog)
        self.serverLineEdit.setObjectName("serverLineEdit")
        self.gridLayout.addWidget(self.serverLineEdit, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 2, 1, 1)
        self.portLineEdit = QtWidgets.QLineEdit(Dialog)
        self.portLineEdit.setObjectName("portLineEdit")
        self.gridLayout.addWidget(self.portLineEdit, 0, 3, 1, 2)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Connect to TSC"))
        self.label.setText(_translate("Dialog", "Server"))
        self.serverLineEdit.setText(_translate("Dialog", "127.0.0.1"))
        self.label_2.setText(_translate("Dialog", "Port"))
        self.portLineEdit.setText(_translate("Dialog", "9001"))
