# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pklz_viewer.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import cPickle
import gzip

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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setWindowModality(QtCore.Qt.WindowModal)
        MainWindow.resize(956, 756)
        MainWindow.setMaximumSize(QtCore.QSize(323232, 323232))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8(":/main/extrude.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter_3 = QtGui.QSplitter(self.centralwidget)
        self.splitter_3.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_3.setObjectName(_fromUtf8("splitter_3"))
        self.splitter_2 = QtGui.QSplitter(self.splitter_3)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.listView = QtGui.QListView(self.splitter_2)
        self.listView.setMaximumSize(QtCore.QSize(400, 16777215))
        self.listView.setObjectName(_fromUtf8("listView"))
        self.splitter = QtGui.QSplitter(self.splitter_3)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget.setMaximumSize(QtCore.QSize(16777215, 200))
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.treeWidget.header().setHighlightSections(True)
        self.verticalLayout.addWidget(self.splitter_3)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 956, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menu_Help = QtGui.QMenu(self.menubar)
        self.menu_Help.setObjectName(_fromUtf8("menu_Help"))
        self.menuAction = QtGui.QMenu(self.menubar)
        self.menuAction.setObjectName(_fromUtf8("menuAction"))
        self.menuSetting = QtGui.QMenu(self.menubar)
        self.menuSetting.setObjectName(_fromUtf8("menuSetting"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.dockWidget = QtGui.QDockWidget(MainWindow)
        self.dockWidget.setObjectName(_fromUtf8("dockWidget"))
        self.dockWidgetContents = QtGui.QWidget()
        self.dockWidgetContents.setObjectName(_fromUtf8("dockWidgetContents"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.dockWidgetContents)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.listWidget = QtGui.QListWidget(self.dockWidgetContents)
        self.listWidget.setObjectName(_fromUtf8("listWidget"))
        self.horizontalLayout.addWidget(self.listWidget)
        self.dockWidget.setWidget(self.dockWidgetContents)
        MainWindow.addDockWidget(QtCore.Qt.DockWidgetArea(8), self.dockWidget)
        self.action_Open = QtGui.QAction(MainWindow)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(_fromUtf8(":/fileopen/images/fileopen.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.action_Open.setIcon(icon1)
        self.action_Open.setObjectName(_fromUtf8("action_Open"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionPrevious = QtGui.QAction(MainWindow)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(_fromUtf8(":/Left/images/Left.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionPrevious.setIcon(icon2)
        self.actionPrevious.setMenuRole(QtGui.QAction.AboutQtRole)
        self.actionPrevious.setObjectName(_fromUtf8("actionPrevious"))
        self.actionNext = QtGui.QAction(MainWindow)
        icon3 = QtGui.QIcon()
        icon3.addPixmap(QtGui.QPixmap(_fromUtf8(":/Right/images/Right.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.actionNext.setIcon(icon3)
        self.actionNext.setObjectName(_fromUtf8("actionNext"))
        self.actionSet_IDB = QtGui.QAction(MainWindow)
        self.actionSet_IDB.setObjectName(_fromUtf8("actionSet_IDB"))
        self.actionSave = QtGui.QAction(MainWindow)
        self.actionSave.setObjectName(_fromUtf8("actionSave"))
        self.actionLog = QtGui.QAction(MainWindow)
        self.actionLog.setObjectName(_fromUtf8("actionLog"))
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.actionSave)
        self.menu_File.addAction(self.actionExit)
        self.menu_Help.addAction(self.actionAbout)
        self.menuAction.addAction(self.actionPrevious)
        self.menuAction.addAction(self.actionNext)
        self.menuAction.addAction(self.actionLog)
        self.menuSetting.addAction(self.actionSet_IDB)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menuAction.menuAction())
        self.menubar.addAction(self.menuSetting.menuAction())
        self.menubar.addAction(self.menu_Help.menuAction())
        self.toolBar.addAction(self.action_Open)
        self.toolBar.addSeparator()
        self.toolBar.addAction(self.actionPrevious)
        self.toolBar.addAction(self.actionNext)

        self.retranslateUi(MainWindow)
        #QtCore.QObject.connect(self.action_Open, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.update)
        #QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.actionExit.triggered.connect(MainWindow.close)

        self.action_Open.triggered.connect(self.openFile)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('Name','Description'))
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.tree_header=QtGui.QTreeWidgetItem(['Name','description','raw','Eng value'])
        self.treeWidget.setHeaderItem(self.tree_header)
        self.actionNext.triggered.connect(self.next)
        self.actionPrevious.triggered.connect(self.previous)
        self.actionAbout.triggered.connect(self.about)

        self.actionLog.triggered.connect(self.dockWidget.show)
    def about(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setIcon(QtGui.QMessageBox.Information)
        msgBox.setText("STIX PKLZ file viewer, hualin.xiao@fhnw.ch")
        msgBox.setWindowTitle("Stix PKLZ file viewer")
        msgBox.setStandardButtons(QtGui.QMessageBox.Ok)
        msgBox.exec_()


    def next(self):
        self.current_row+=1
        self.showPacket(self.current_row)
    def previous(self):
        self.current_row-=1
        self.showPacket(self.current_row)

    def openFile(self):
        filename = QtGui.QFileDialog.getOpenFileName(None,'Select file', '/home', 'pkl files (*.pkl *.pklz)')
        self.readData(filename)
    def addLogEntry(self,msg):
        self.listWidget.addItem(msg)
    def readData(self,filename):
        self.statusbar.showMessage('Opening file %s'%filename)
        self.addLogEntry('Opening file %s'%filename)
        f=gzip.open(filename,'rb')
        self.addLogEntry('File uncompressed ...')
        self.data=cPickle.load(f)['packet']
        self.addLogEntry('Data loaded')
        f.close()
        self.model = QtGui.QStandardItemModel()
        for p in self.data:
            header=p['header']
            msg='TM(%d,%d) - %s'%(header['service_type'],header['service_subtype'],header['DESCR'])
            #print msg
            self.model.appendRow(QtGui.QStandardItem(msg))
        self.listView.setModel(self.model)
        self.total_packets=len(self.data)
        self.statusbar.showMessage('%d packets loaded'%(self.total_packets))
        self.addLogEntry('%d packets loaded'%(self.total_packets))
        self.listView.selectionModel().currentChanged.connect(self.packetSelected)
        self.tableWidget.setRowCount(0)
        self.showHeader(0)
        self.showParameter(0)
    
    def packetSelected(self, current, previous):
        self.current_row=current.row()
        self.statusbar.showMessage('Packet %d selected' % self.current_row)
        self.showPacket(self.current_row)

    def showPacket(self,row):
        self.showHeader(row)
        self.showParameter(row)

    def showHeader(self,row):
        if not self.data:
            return
        header=self.data[row]['header']
        self.statusbar.showMessage('Packet %d / %d  %s ' % (row, self.total_packets, header['DESCR']))

        rows=len(header)
        self.tableWidget.setRowCount(rows)
        i=0
        for key, val in header.items():
            self.tableWidget.setItem(i,0,QtGui.QTableWidgetItem(key))
            self.tableWidget.setItem(i,1,QtGui.QTableWidgetItem(str(val)))
            i += 1

    def showParameter(self,row):
        if not self.data:
            return
        params=self.data[row]['parameter']
        self.treeWidget.clear()
        self.showParameterTree(params,self.treeWidget)

    def showParameterTree(self, params, parent):
        for p in  params:
            root=QtGui.QTreeWidgetItem(parent)
            try:
                root.setText(0,p['name'])
                root.setText(1,p['descr'])
                root.setText(2,str(p['raw']))
                root.setText(3,str(p['value']))
                if 'child' in p:
                    if p['child']:
                        self.showParameterTree(p['child'],root)
            except KeyError:
                self.addLogEntry('Error: keyError adding parameter')
                


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "STIX data parser and viewer", None))
        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.menu_Help.setTitle(_translate("MainWindow", "&Help", None))
        self.menuAction.setTitle(_translate("MainWindow", "&View", None))
        self.menuSetting.setTitle(_translate("MainWindow", "&Setting", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.dockWidget.setWindowTitle(_translate("MainWindow", "Log", None))
        self.action_Open.setText(_translate("MainWindow", "&Open", None))
        self.actionExit.setText(_translate("MainWindow", "&Exit", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionPrevious.setText(_translate("MainWindow", "Previous", None))
        self.actionNext.setText(_translate("MainWindow", "Next", None))
        self.actionSet_IDB.setText(_translate("MainWindow", "Set &IDB", None))
        self.actionSave.setText(_translate("MainWindow", "Sa&ve", None))
        self.actionLog.setText(_translate("MainWindow", "Show Log", None))

import viewer_rc
