# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plugin.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

import os
import sys
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(493, 264)
        self.Dialog=Dialog
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(Dialog)
        self.label_2.setMaximumSize(QtCore.QSize(100, 16777215))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.folderLineEdit = QtWidgets.QLineEdit(Dialog)
        self.folderLineEdit.setObjectName("folderLineEdit")
        self.gridLayout.addWidget(self.folderLineEdit, 0, 1, 1, 4)
        self.folderToolButton = QtWidgets.QToolButton(Dialog)
        self.folderToolButton.setMaximumSize(QtCore.QSize(50, 16777215))
        self.folderToolButton.setObjectName("folderToolButton")
        self.gridLayout.addWidget(self.folderToolButton, 0, 5, 1, 1)
        self.label = QtWidgets.QLabel(Dialog)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 1, 0, 1, 3)
        self.editPushButton = QtWidgets.QPushButton(Dialog)
        self.editPushButton.setObjectName("editPushButton")
        self.gridLayout.addWidget(self.editPushButton, 3, 0, 1, 2)
        self.newPushButton= QtWidgets.QPushButton(Dialog)
        self.newPushButton.setObjectName("newPushButton")
        self.gridLayout.addWidget(self.newPushButton, 3, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 3, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply|QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 4, 1, 2)
        self.pluginListWidget = QtWidgets.QListWidget(Dialog)
        self.pluginListWidget.setObjectName("pluginListWidget")
        self.gridLayout.addWidget(self.pluginListWidget, 2, 0, 1, 6)
        self.verticalLayout.addLayout(self.gridLayout)

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.folderToolButton.clicked.connect(self.changeFolder)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.applyButton=self.buttonBox.button(QtWidgets.QDialogButtonBox.Apply)
        self.applyButton.clicked.connect(self.apply)
        self.editPushButton.clicked.connect(self.edit)
        self.newPushButton.clicked.connect(self.createNew)

        self.data=None
        self.current_row=0
    def setData(self, data,row):
        self.data=data
        self.current_row=row

    def apply(self):
        fname=self.pluginListWidget.currentItem().text()
        if not fname:
            return 
        path=self.getPluginLocation()
        abs_fname=os.path.join(path,fname)
        try:
            from importlib import import_module
            name, ext = os.path.splitext(fname)
            sys.path.insert(0, path)
            mod = __import__(name)
            plugin = mod.Plugin(self.data, self.current_row)
            plugin.run()
            sys.path.pop(0)
        except Exception as e:
            print(e)
        

    def edit(self):
        path=self.getPluginLocation()
        fname=self.pluginListWidget.currentItem().text()
        if fname:
            return
        abs_fname=os.path.join(path,fname)
        editor="gedit "
        ret_val = os.system("{} {}".format(editor,abs_fname))
    def createNew(self):
        editor="gedit "
        ret_val = os.system("{} ".format(editor))

    def changeFolder(self, default_folder=''):
        folder=default_folder
        if not default_folder:
            folder=os.path.expanduser('~')
        loc= str(QtWidgets.QFileDialog.getExistingDirectory(
            self.Dialog,
            "Open plugin folder",
            folder,
            QtWidgets.QFileDialog.ShowDirsOnly
            ))
        self.setPluginLocation(loc)

    def setPluginLocation(self,loc):
        self.folderLineEdit.setText(loc)
        self.openPluginFolder()
    def getPluginLocation(self):
        return self.folderLineEdit.text()
    def openPluginFolder(self):
        self.pluginListWidget.clear()
        path=self.folderLineEdit.text()
        try:
            for f in os.listdir(path):
                fname, ext = os.path.splitext(f)
                if ext == '.py':
                    self.pluginListWidget.addItem(fname+'.py')
        except:
            pass

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Plugins"))
        self.label_2.setText(_translate("Dialog", "Location:"))
        self.folderLineEdit.setText(_translate("Dialog", "../plugins/"))
        self.folderToolButton.setText(_translate("Dialog", "..."))
        self.label.setText(_translate("Dialog", "Available plugins:"))
        self.editPushButton.setText(_translate("Dialog", "Edit"))
        self.newPushButton.setText(_translate("Dialog", "New"))


