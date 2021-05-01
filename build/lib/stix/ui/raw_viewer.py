# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/raw_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

NUM_BYTES_EACH_ROW = 16


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(550, 283)
        Dialog.setMinimumSize(QtCore.QSize(550, 0))
        Dialog.setMaximumSize(QtCore.QSize(1000, 5000))
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.packetInfo = QtWidgets.QLabel(Dialog)
        self.packetInfo.setText("")
        self.packetInfo.setObjectName("packetInfo")
        self.verticalLayout.addWidget(self.packetInfo)
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.textEdit.setFont(font)
        self.textEdit.setAutoFillBackground(False)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.msg = QtWidgets.QLabel(Dialog)
        self.msg.setMaximumSize(QtCore.QSize(500, 250))
        self.msg.setText("")
        self.msg.setObjectName("msg")
        self.horizontalLayout.addWidget(self.msg)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setMaximumSize(QtCore.QSize(100, 16777215))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.horizontalLayout.addWidget(self.buttonBox)
        self.verticalLayout.addLayout(self.horizontalLayout)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        self.textEdit.cursorPositionChanged.connect(Dialog.update)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

        self.textEdit.cursorPositionChanged.connect(
            self.onCursorPositionChanged)
        self.dataShown = False
        self.Dialog = Dialog

    def onCursorPositionChanged(self):
        if not self.dataShown:
            return
        cursor = self.textEdit.textCursor()
        pos = cursor.position()
        num_rows = int(pos / (4 * NUM_BYTES_EACH_ROW + 1))
        ibyte = int((pos - num_rows) / 4)
        self.msg.setText('Length: {:<5} Offset: {:<5}'.format(
            self.length, ibyte))
        self.msg.update()

    def setPacketInfo(self, text):
        self.packetInfo.setText(text)

    def setText(self, text):
        self.textEdit.setText(text)

    def displayRaw(self, raw):
        self.dataShown = True
        self.length = len(raw)
        text = ''
        for i, h in enumerate(raw):
            text += '{:02X}  '.format(h)
            if i > 0 and (i + 1) % NUM_BYTES_EACH_ROW == 0:
                text += '\n'
        self.setText(text)
        self.msg.setText('Length: {} '.format(self.length))

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Packet raw data"))
