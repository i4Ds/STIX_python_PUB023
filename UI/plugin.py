# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plugin.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

import os
from io import StringIO
import sys
import importlib
import tempfile
import webbrowser
from PyQt5 import QtCore, QtGui, QtWidgets

PLUGIN_TEMPLATE = """
#!/usr/bin/python3
#plugin template
class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
    def run(self):
        # your code goes here
        print('current row: {}'.format(self.current_row))
        print('Number of packets {}:'.format(len(self.packets)))
        print(len(self.packets))
        for packet in self.packets:
            print(str(packet))
"""


def createTemplate(path):
    filename = 'Unititled_{}.py'
    if path:
        filename = os.path.join(path, 'Untitled_{}.py')
    counter = 0
    while os.path.isfile(filename.format(counter)):
        counter += 1
    fname = filename.format(counter)
    try:
        f = open(fname, 'w')
        f.write(PLUGIN_TEMPLATE)
        f.close()
    except IOError:
        f = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        f.write(PLUGIN_TEMPLATE)
        fname = f.name
        f.close()
    return fname


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(583, 506)
        self.horizontalLayout = QtWidgets.QHBoxLayout(Dialog)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout = QtWidgets.QVBoxLayout()
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
        self.newPushButton = QtWidgets.QPushButton(Dialog)
        self.newPushButton.setObjectName("newPushButton")
        self.gridLayout.addWidget(self.newPushButton, 3, 2, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20,
                                           QtWidgets.QSizePolicy.Expanding,
                                           QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 3, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Apply
                                          | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 3, 4, 1, 2)
        self.pluginListWidget = QtWidgets.QListWidget(Dialog)
        self.pluginListWidget.setObjectName("pluginListWidget")
        self.gridLayout.addWidget(self.pluginListWidget, 2, 0, 1, 6)
        self.verticalLayout.addLayout(self.gridLayout)
        self.label_3 = QtWidgets.QLabel(Dialog)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.textBrowser = QtWidgets.QTextBrowser(Dialog)
        self.textBrowser.setObjectName("textBrowser")
        self.verticalLayout.addWidget(self.textBrowser)
        self.horizontalLayout.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.Dialog = Dialog

        self.folderToolButton.clicked.connect(self.changeFolder)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.applyButton = self.buttonBox.button(
            QtWidgets.QDialogButtonBox.Apply)
        self.applyButton.clicked.connect(self.apply)
        self.editPushButton.clicked.connect(self.edit)
        self.newPushButton.clicked.connect(self.createNew)

        self.packets = None
        self.current_row = 0

    def setData(self, packets, row):
        self.packets = packets
        self.current_row = row

    def apply(self):
        self.textBrowser.clear()
        try:
            fname = self.pluginListWidget.currentItem().text()
        except AttributeError:
            return

        if not fname:
            return
        path = self.getPluginLocation()
        abs_fname = os.path.join(path, fname)
        try:
            name, ext = os.path.splitext(fname)
            sys.path.insert(0, path)
            mod = importlib.import_module(name)
            importlib.reload(mod)
            sys.path.pop(0)
            plugin = mod.Plugin(self.packets, self.current_row)
            old_stdout = sys.stdout
            print_out = StringIO()
            sys.stdout = print_out
            plugin.run()
            msg = print_out.getvalue()
            sys.stdout = old_stdout
            if msg:
                self.textBrowser.setText(msg)
        except Exception as e:
            self.textBrowser.setText(str(e))

    def edit(self):
        path = self.getPluginLocation()
        try:
            fname = self.pluginListWidget.currentItem().text()
        except AttributeError:
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Error")
            msg.setText("No plugin selected!")
            msg.setWindowTitle("Error")
            msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
            retval = msg.exec_()
            return

        abs_fname = os.path.join(path, fname)
        webbrowser.open(abs_fname)

    def createNew(self):
        try:
            folder = self.getPluginLocation()
            new_filename = createTemplate(folder)
            webbrowser.open(new_filename)
        except Exception as e:
            print(e)
        self.updatePluginList()

    def changeFolder(self, default_folder=''):
        folder = default_folder
        if not folder:
            folder = self.getPluginLocation()
            if not folder:
                folder = os.path.expanduser('~')
        loc = str(
            QtWidgets.QFileDialog.getExistingDirectory(
                self.Dialog, "Open plugin folder", folder,
                QtWidgets.QFileDialog.ShowDirsOnly))
        self.setPluginLocation(loc)

    def setPluginLocation(self, loc):
        self.folderLineEdit.setText(loc)
        self.updatePluginList()

    def getPluginLocation(self):
        return self.folderLineEdit.text()

    def updatePluginList(self):
        self.pluginListWidget.clear()
        path = self.folderLineEdit.text()
        try:
            for f in os.listdir(path):
                fname, ext = os.path.splitext(f)
                if ext == '.py':
                    self.pluginListWidget.addItem(fname + '.py')
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
        self.label_3.setText(_translate("Dialog", "Outputs:"))
