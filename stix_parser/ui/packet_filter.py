# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'packet_filter.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

import re
from PyQt5 import QtCore, QtGui, QtWidgets

SERVICES = [1, 3, 5, 6, 9, 17, 20, 21, 22, 236, 237, 238, 239]
SERVICES_DESCRIPTION = [
    "Service 1 (TC verification)",
    "Service 3 (HK)", 
    "Service 5 (Event reporting)", "Service 6 (memory)",
    "Service 9 (Time management)", "Service 17 (connection test)",
    "Service 20 (Platform information)", "Service 21 (science)",
    "Service 22 (context)", "Service 236 (configuration)",
    "Service 237 (parameters)", "Service 238 (archive)",
    "Service 239 (test and debug)"
]


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(643, 327)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setObjectName("groupBox")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.checkBoxSelectAll = QtWidgets.QCheckBox(self.groupBox)
        self.checkBoxSelectAll.setChecked(True)
        self.checkBoxSelectAll.setObjectName("checkBoxSelectAll")
        self.gridLayout.addWidget(self.checkBoxSelectAll, 0, 0, 1, 2)

        self.checkBoxes = []
        for i, service in enumerate(SERVICES):
            checkBox = QtWidgets.QCheckBox(self.groupBox)
            checkBox.setChecked(True)
            checkBox.setObjectName('checkbox' + str(service))
            row = i / 2
            col = i % 2
            self.gridLayout.addWidget(checkBox, row + 1, col, 1, 1)
            self.checkBoxes.append(checkBox)

        self.horizontalLayout.addLayout(self.gridLayout)
        self.verticalLayout.addWidget(self.groupBox)
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.lineEditSPID = QtWidgets.QLineEdit(Dialog)
        self.lineEditSPID.setObjectName("lineEditSPID")
        self.horizontalLayout_2.addWidget(self.lineEditSPID)
        spacerItem = QtWidgets.QSpacerItem(188, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel
                                          | QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.checkBoxSelectAll.stateChanged.connect(self.checkBoxStateChanged)
        self.checkBoxSelectAll.stateChanged.connect(self.checkBoxStateChanged)
        self.lineEditSPID.textChanged.connect(self.SPIDChanged)

    def SPIDChanged(self):
        self.selectNone()
        self.checkBoxSelectAll.setChecked(False)

    def checkBoxStateChanged(self):
        is_checked = self.checkBoxSelectAll.isChecked()
        if is_checked:
            self.selectAll()
        else:
            self.selectNone()

    def getSelectedSPID(self):
        SPID_text = self.lineEditSPID.text()
        if SPID_text == '*':
            return []
        return [int(s) for s in re.findall(r'\d+', SPID_text)]

    def getSelectedServices(self):
        services = []
        for i, checkBox in enumerate(self.checkBoxes):
            if checkBox.isChecked():
                services.append(SERVICES[i])
        return services

    def setSelectedServices(self, services):
        for ser in services:
            try:
                index = services.index(ser)
                self.checkBoxes[index].setChecked(True)
            except ValueError:
                pass

    def selectAll(self):
        for checkBox in self.checkBoxes:
            checkBox.setChecked(True)

    def selectNone(self):
        for checkBox in self.checkBoxes:
            checkBox.setChecked(False)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Packet filtering"))
        self.groupBox.setTitle(_translate("Dialog", "Selection by services"))
        self.checkBoxSelectAll.setText(_translate("Dialog", "All services"))
        self.label.setText(_translate("Dialog", "or by SPID(s):"))
        self.lineEditSPID.setText(_translate("Dialog", "*"))

        for i, checkBox in enumerate(self.checkBoxes):
            checkBox.setText(_translate("Dialog", SERVICES_DESCRIPTION[i]))
