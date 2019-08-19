# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'service_filter.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'service_filter.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(554, 250)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.pushButtonAll = QtWidgets.QPushButton(Dialog)
        self.pushButtonAll.setObjectName("pushButtonAll")
        self.gridLayout.addWidget(self.pushButtonAll, 0, 0, 1, 1)
        self.pushButtonNone = QtWidgets.QPushButton(Dialog)
        self.pushButtonNone.setObjectName("pushButtonNone")
        self.gridLayout.addWidget(self.pushButtonNone, 0, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(168, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 2, 1, 2)
        self.checkBoxS1 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS1.setChecked(True)
        self.checkBoxS1.setObjectName("checkBoxS1")
        self.gridLayout.addWidget(self.checkBoxS1, 1, 0, 1, 3)
        self.checkBoxS3 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS3.setChecked(True)
        self.checkBoxS3.setObjectName("checkBoxS3")
        self.gridLayout.addWidget(self.checkBoxS3, 1, 3, 1, 1)
        self.checkBoxS5 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS5.setChecked(True)
        self.checkBoxS5.setObjectName("checkBoxS5")
        self.gridLayout.addWidget(self.checkBoxS5, 2, 0, 1, 3)
        self.checkBoxS6 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS6.setChecked(True)
        self.checkBoxS6.setObjectName("checkBoxS6")
        self.gridLayout.addWidget(self.checkBoxS6, 2, 3, 1, 1)
        self.checkBoxS17 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS17.setChecked(True)
        self.checkBoxS17.setObjectName("checkBoxS17")
        self.gridLayout.addWidget(self.checkBoxS17, 3, 0, 1, 3)
        self.checkBoxS21 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS21.setChecked(True)
        self.checkBoxS21.setObjectName("checkBoxS21")
        self.gridLayout.addWidget(self.checkBoxS21, 3, 3, 1, 1)
        self.checkBoxS22 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS22.setChecked(True)
        self.checkBoxS22.setObjectName("checkBoxS22")
        self.gridLayout.addWidget(self.checkBoxS22, 4, 0, 1, 2)
        self.checkBoxS236 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS236.setChecked(True)
        self.checkBoxS236.setObjectName("checkBoxS236")
        self.gridLayout.addWidget(self.checkBoxS236, 4, 3, 1, 1)
        self.checkBoxS237 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS237.setChecked(True)
        self.checkBoxS237.setObjectName("checkBoxS237")
        self.gridLayout.addWidget(self.checkBoxS237, 5, 0, 1, 3)
        self.checkBoxS238 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS238.setChecked(True)
        self.checkBoxS238.setObjectName("checkBoxS238")
        self.gridLayout.addWidget(self.checkBoxS238, 5, 3, 1, 1)
        self.checkBoxS239 = QtWidgets.QCheckBox(Dialog)
        self.checkBoxS239.setChecked(True)
        self.checkBoxS239.setObjectName("checkBoxS239")
        self.gridLayout.addWidget(self.checkBoxS239, 6, 0, 1, 4)
        self.verticalLayout.addLayout(self.gridLayout)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)



        self.pushButtonAll.clicked.connect(self.selectAll)
        self.pushButtonNone.clicked.connect(self.selectNone)


    def getSelectedServices(self):
        services=[]
        if self.checkBoxS1.isChecked():
            services.append(1)
        if self.checkBoxS3.isChecked():
            services.append(3)
        if self.checkBoxS6.isChecked():
            services.append(6)
        if self.checkBoxS17.isChecked():
            services.append(17)
        if self.checkBoxS21.isChecked():
            services.append(21)
        if self.checkBoxS22.isChecked():
            services.append(22)
        if self.checkBoxS236.isChecked():
            services.append(236)
        if self.checkBoxS237.isChecked():
            services.append(237)
        if self.checkBoxS238.isChecked():
            services.append(238)
        if self.checkBoxS239.isChecked():
            services.append(239)
        if self.checkBoxS5.isChecked():
            services.append(5)

        return services
    def setSelectedServices(self,services):
        self.checkBoxS1.setChecked(1 in services)
        self.checkBoxS3.setChecked(3 in services)
        self.checkBoxS6.setChecked(6 in services)
        self.checkBoxS17.setChecked(17 in services)
        self.checkBoxS21.setChecked(21 in services)
        self.checkBoxS22.setChecked(22 in services)
        self.checkBoxS236.setChecked(236 in services)
        self.checkBoxS237.setChecked(237 in services)
        self.checkBoxS238.setChecked(238 in services)
        self.checkBoxS239.setChecked(239 in services)
        self.checkBoxS5.setChecked(5 in services)

        
    def selectAll(self):
        self.checkBoxS1.setChecked(True)
        self.checkBoxS3.setChecked(True)
        self.checkBoxS6.setChecked(True)
        self.checkBoxS17.setChecked(True)
        self.checkBoxS21.setChecked(True)
        self.checkBoxS22.setChecked(True)
        self.checkBoxS236.setChecked(True)
        self.checkBoxS237.setChecked(True)
        self.checkBoxS238.setChecked(True)
        self.checkBoxS239.setChecked(True)
        self.checkBoxS5.setChecked(True)
    def selectNone(self):
        self.checkBoxS5.setChecked(False)
        self.checkBoxS1.setChecked(False)
        self.checkBoxS3.setChecked(False)
        self.checkBoxS6.setChecked(False)
        self.checkBoxS17.setChecked(False)
        self.checkBoxS21.setChecked(False)
        self.checkBoxS22.setChecked(False)
        self.checkBoxS236.setChecked(False)
        self.checkBoxS237.setChecked(False)
        self.checkBoxS238.setChecked(False)
        self.checkBoxS239.setChecked(False)



    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Packet filter"))
        self.pushButtonAll.setText(_translate("Dialog", "All"))
        self.pushButtonNone.setText(_translate("Dialog", "None"))
        self.checkBoxS1.setText(_translate("Dialog", "Service 1 (TC verification)"))
        self.checkBoxS3.setText(_translate("Dialog", "Service 3 (HK)"))
        self.checkBoxS5.setText(_translate("Dialog", "Service 5 (Event reporting)"))
        self.checkBoxS6.setText(_translate("Dialog", "Service 6 (memory)"))
        self.checkBoxS17.setText(_translate("Dialog", "Service 17 (connection test)"))
        self.checkBoxS21.setText(_translate("Dialog", "Service 21 (science)"))
        self.checkBoxS22.setText(_translate("Dialog", "Service 22 (context)"))
        self.checkBoxS236.setText(_translate("Dialog", "Service 236 (configuration)"))
        self.checkBoxS237.setText(_translate("Dialog", "Service 237 (parameters)"))
        self.checkBoxS238.setText(_translate("Dialog", "Service 238 (archive)"))
        self.checkBoxS239.setText(_translate("Dialog", "Service 239 (test and debug)"))

