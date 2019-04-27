# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pklz_viewer.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui
import gzip
import cPickle

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
        MainWindow.resize(832, 756)
        #MainWindow.setMaximumSize(QtCore.QSize(832, 756))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../../../../../../opencascade/mayo_2019/images/themes/classic/cut.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.centralwidget)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.splitter_2 = QtGui.QSplitter(self.centralwidget)
        self.splitter_2.setOrientation(QtCore.Qt.Horizontal)
        self.splitter_2.setObjectName(_fromUtf8("splitter_2"))
        self.frame_2 = QtGui.QFrame(self.splitter_2)
        self.frame_2.setMinimumSize(QtCore.QSize(200, 0))
        self.frame_2.setMaximumSize(QtCore.QSize(300, 16777215))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.listView = QtGui.QListView(self.frame_2)
        self.listView.setObjectName(_fromUtf8("listView"))
        self.verticalLayout_2.addWidget(self.listView)
        self.frame = QtGui.QFrame(self.splitter_2)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.splitter = QtGui.QSplitter(self.frame)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName(_fromUtf8("splitter"))
        self.tableWidget = QtGui.QTableWidget(self.splitter)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.treeWidget = QtGui.QTreeWidget(self.splitter)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.verticalLayout.addWidget(self.splitter)
        self.verticalLayout_3.addWidget(self.splitter_2)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 832, 22))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menu_File = QtGui.QMenu(self.menubar)
        self.menu_File.setObjectName(_fromUtf8("menu_File"))
        self.menu_About = QtGui.QMenu(self.menubar)
        self.menu_About.setObjectName(_fromUtf8("menu_About"))
        self.menuAction = QtGui.QMenu(self.menubar)
        self.menuAction.setObjectName(_fromUtf8("menuAction"))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.toolBar = QtGui.QToolBar(MainWindow)
        self.toolBar.setObjectName(_fromUtf8("toolBar"))
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_Open = QtGui.QAction(MainWindow)
        self.action_Open.setObjectName(_fromUtf8("action_Open"))
        self.actionExit = QtGui.QAction(MainWindow)
        self.actionExit.setObjectName(_fromUtf8("actionExit"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionPrevious = QtGui.QAction(MainWindow)
        self.actionPrevious.setObjectName(_fromUtf8("actionPrevious"))
        self.actionNext = QtGui.QAction(MainWindow)
        self.actionNext.setObjectName(_fromUtf8("actionNext"))
        self.menu_File.addAction(self.action_Open)
        self.menu_File.addAction(self.actionExit)
        self.menu_About.addAction(self.actionAbout)
        self.menuAction.addAction(self.actionPrevious)
        self.menuAction.addAction(self.actionNext)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menuAction.menuAction())
        self.menubar.addAction(self.menu_About.menuAction())
        self.toolBar.addAction(self.action_Open)
        self.toolBar.addAction(self.actionPrevious)
        self.toolBar.addAction(self.actionNext)

        self.retranslateUi(MainWindow)
        QtCore.QObject.connect(self.action_Open, QtCore.SIGNAL(_fromUtf8("triggered()")), MainWindow.update)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.action_Open.triggered.connect(self.openFile)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('Name','Description'))
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)

        self.tree_header=QtGui.QTreeWidgetItem(['Name','description','raw','Eng value'])
        self.treeWidget.setHeaderItem(self.tree_header)
        self.actionNext.triggered.connect(self.next)
        self.actionPrevious.triggered.connect(self.previous)

    def next(self):
        self.current_row+=1
        self.showPacket(self.current_row)
    def previous(self):
        self.current_row-=1
        self.showPacket(self.current_row)

    def openFile(self):
        filename = QtGui.QFileDialog.getOpenFileName(None,'Select file', '/home', 'pkl files (*.pkl *.pklz)')
        self.statusbar.showMessage('File %s'%filename)
        
        self.readData(filename)
    def readData(self,filename):
        f=gzip.open(filename,'rb')
        self.data=cPickle.load(f)['packet']

        f.close()
        self.model = QtGui.QStandardItemModel()
        for p in self.data:
            header=p['header']
            msg='TM(%d,%d) - %s'%(header['service_type'],header['service_subtype'],header['DESCR'])
            print msg
            self.model.appendRow(QtGui.QStandardItem(msg))
        self.listView.setModel(self.model)
        self.total_packets=len(self.data)
        self.statusbar.showMessage('%d packets loaded'%(self.total_packets))
        self.listView.selectionModel().currentChanged.connect(self.packetSelected)
        self.tableWidget.setRowCount(0)
        self.showPacket(0)
    
    def packetSelected(self, current, previous):
        self.current_row=current.row()
        self.statusbar.showMessage('Packet %d selected' % self.current_row)
        self.showPacket(self.current_row)

    def showPacket(self,row):
        if not self.data:
            return
        self.statusbar.showMessage('Packet %d / %d ' % (row, self.total_packets))
        params=self.data[row]['parameter']
        self.treeWidget.clear()
        header=self.data[row]['header']

        root=QtGui.QTreeWidgetItem(self.treeWidget)

        packetheaderItem=QtGui.QTreeWidgetItem(root)
        packetheaderItem.setText(0,'Header')
        parameterItem=QtGui.QTreeWidgetItem(root)
        parameterItem.setText(0,'Parameters')

        for key, val in header.items():
            headerRoot=QtGui.QTreeWidgetItem(packetheaderItem)
            headerRoot.setText(0,key)
            headerROOT.setText(2,str(val))
            print(val)

        self.showParameterTree(params,parameterItem)

    def showParameterTree(self, params, parent):
        for p in  params:
            root=QtGui.QTreeWidgetItem(parent)
            root.setText(0,p['name'])
            root.setText(1,p['descr'])
            root.setText(2,str(p['raw']))
            root.setText(3,str(p['value']))
            if 'child' in p:
                if p['child']:
                    self.showParameterTree(p['child'],root)


    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "STIX PKLZ viewer", None))
        self.menu_File.setTitle(_translate("MainWindow", "&File", None))
        self.menu_About.setTitle(_translate("MainWindow", "&About", None))
        self.menuAction.setTitle(_translate("MainWindow", "Action", None))
        self.toolBar.setWindowTitle(_translate("MainWindow", "toolBar", None))
        self.action_Open.setText(_translate("MainWindow", "&Open", None))
        self.actionExit.setText(_translate("MainWindow", "Exit", None))
        self.actionAbout.setText(_translate("MainWindow", "About", None))
        self.actionPrevious.setText(_translate("MainWindow", "Previous", None))
        self.actionNext.setText(_translate("MainWindow", "Next", None))

