# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'clipboard.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import sys
import binascii
import re
from tools import parser
from cStringIO import StringIO
from stix_io import stix_logger



try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        mainWindow.setObjectName(_fromUtf8("mainWindow"))
        mainWindow.setEnabled(True)
        mainWindow.resize(653, 799)
        mainWindow.setStyleSheet(_fromUtf8("border-color: rgb(138, 226, 52);"))
        self.centralwidget = QtGui.QWidget(mainWindow)
        self.centralwidget.setStyleSheet(_fromUtf8(""))
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setObjectName(_fromUtf8("label"))
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.textEdit = QtGui.QTextEdit(self.centralwidget)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.textEdit.sizePolicy().hasHeightForWidth())
        self.textEdit.setSizePolicy(sizePolicy)
        self.textEdit.setMinimumSize(QtCore.QSize(0, 200))
        self.textEdit.setObjectName(_fromUtf8("textEdit"))
        self.gridLayout.addWidget(self.textEdit, 1, 0, 1, 4)
        self.clearButton = QtGui.QPushButton(self.centralwidget)
        self.clearButton.setMinimumSize(QtCore.QSize(0, 20))
        self.clearButton.setObjectName(_fromUtf8("clearButton"))
        self.gridLayout.addWidget(self.clearButton, 2, 0, 1, 1)
        spacerItem = QtGui.QSpacerItem(98, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 2, 1, 1, 1)
        self.pasteButton = QtGui.QPushButton(self.centralwidget)
        self.pasteButton.setMinimumSize(QtCore.QSize(150, 20))
        self.pasteButton.setObjectName(_fromUtf8("pasteButton"))
        self.gridLayout.addWidget(self.pasteButton, 2, 2, 1, 1)
        self.parseButton = QtGui.QPushButton(self.centralwidget)
        self.parseButton.setMinimumSize(QtCore.QSize(0, 20))
        self.parseButton.setObjectName(_fromUtf8("parseButton"))
        self.gridLayout.addWidget(self.parseButton, 2, 3, 1, 1)
        self.tableWidget = QtGui.QTableWidget(self.centralwidget)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(4)

        self.tableWidget.setHorizontalHeaderLabels(('Name','Description','Raw','Eng_Value'))
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.gridLayout.addWidget(self.tableWidget, 5, 0, 1, 4)
        self.status = QtGui.QLabel(self.centralwidget)
        self.status.setMinimumSize(QtCore.QSize(200, 20))
        self.status.setText(_fromUtf8(""))
        self.status.setObjectName(_fromUtf8("status"))
        self.gridLayout.addWidget(self.status, 6, 0, 1, 2)
        spacerItem1 = QtGui.QSpacerItem(308, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem1, 6, 2, 1, 2)
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.gridLayout.addWidget(self.label_2, 3, 0, 1, 1)
        self.SPIDLabel = QtGui.QLabel(self.centralwidget)
        self.SPIDLabel.setText(_fromUtf8(""))
        self.SPIDLabel.setObjectName(_fromUtf8("SPIDLabel"))
        self.gridLayout.addWidget(self.SPIDLabel, 3, 3, 1, 1)
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.gridLayout.addWidget(self.label_3, 3, 2, 1, 1)
        self.serviceLabel = QtGui.QLabel(self.centralwidget)
        self.serviceLabel.setText(_fromUtf8(""))
        self.serviceLabel.setObjectName(_fromUtf8("serviceLabel"))
        self.gridLayout.addWidget(self.serviceLabel, 3, 1, 1, 1)
        self.label_4 = QtGui.QLabel(self.centralwidget)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.gridLayout.addWidget(self.label_4, 4, 0, 1, 1)
        self.timestampLabel = QtGui.QLabel(self.centralwidget)
        self.timestampLabel.setText(_fromUtf8(""))
        self.timestampLabel.setObjectName(_fromUtf8("timestampLabel"))
        self.gridLayout.addWidget(self.timestampLabel, 4, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout)
        mainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(mainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 653, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        mainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(mainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        mainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(mainWindow)
        QtCore.QObject.connect(self.clearButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.textEdit.clear)
        QtCore.QObject.connect(self.pasteButton, QtCore.SIGNAL(_fromUtf8("clicked()")), self.textEdit.paste)
        QtCore.QMetaObject.connectSlotsByName(mainWindow)
        self.parseButton.clicked.connect(self.parseHex)
    def parseHex(self):
        self.status.setText('Parsing...')
        raw_hex=str(self.textEdit.toPlainText())
        data_hex= re.sub(r"\s+", "", raw_hex)
        if not data_hex:
            self.status.setText('No hex found.')
            return

        try:
            data_binary = binascii.unhexlify(data_hex)
            in_file=StringIO(data_binary)
            status, header, parameters, param_type, num_bytes_read = parser.parse_one_packet(
                in_file, None)
        except TypeError:
            self.status.setText('Failed to parse the packet')
        msg=''
        if header:
            self.serviceLabel.setText('TM(%s, %s)'%(header['service_type'],header['service_subtype']))
            self.SPIDLabel.setText(str(header['SPID']))
            self.timestampLabel.setText(str(header['time']))
        else:
            msg+='Empty header. '
        if parameters:
            self.parlist=[]
            self.add_parameters(parameters)
            rows=len(self.parlist)
            self.tableWidget.setRowCount(rows)

            for i, param in enumerate(self.parlist):
                self.tableWidget.setItem(i,0,QtGui.QTableWidgetItem(str(param['name'])))
                self.tableWidget.setItem(i,1,QtGui.QTableWidgetItem(str(param['descr'])))
                self.tableWidget.setItem(i,2,QtGui.QTableWidgetItem(str(param['raw'])))
                self.tableWidget.setItem(i,3,QtGui.QTableWidgetItem(str(param['value'])))
            else:
                msg+='No parameters. '
            if not msg:
                self.status.setText(msg)
        self.status.setText('Done')

    def add_parameters(self,parameters):
        for par in parameters:
            if par:
                self.parlist.append(par)
                if 'child' in par:
                    if par['child']:
                        self.add_parameters(par['child'])



                





    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(_translate("mainWindow", "MainWindow", None))
        self.label.setText(_translate("mainWindow", "Raw data hex", None))
        self.clearButton.setText(_translate("mainWindow", "Clear", None))
        self.pasteButton.setText(_translate("mainWindow", "Paste from clipboard", None))
        self.parseButton.setText(_translate("mainWindow", "Parse", None))
        self.label_2.setText(_translate("mainWindow", "Service", None))
        self.label_3.setText(_translate("mainWindow", "SPID", None))
        self.label_4.setText(_translate("mainWindow", "Timestamp", None))

