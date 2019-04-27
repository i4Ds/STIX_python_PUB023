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
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../../../../../../opencascade/mayo_2019/images/themes/classic/cut.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.frame_2 = QtGui.QFrame(self.centralwidget)
        self.frame_2.setMinimumSize(QtCore.QSize(200, 0))
        self.frame_2.setMaximumSize(QtCore.QSize(500, 16777215))
        self.frame_2.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtGui.QFrame.Raised)
        self.frame_2.setObjectName(_fromUtf8("frame_2"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.frame_2)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.listView = QtGui.QListView(self.frame_2)
        self.listView.setObjectName(_fromUtf8("listView"))
        self.verticalLayout_2.addWidget(self.listView)
        self.horizontalLayout.addWidget(self.frame_2)
        self.frame = QtGui.QFrame(self.centralwidget)
        self.frame.setFrameShape(QtGui.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtGui.QFrame.Raised)
        self.frame.setObjectName(_fromUtf8("frame"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.frame)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        #self.tableView = QtGui.QTableView(self.frame)
        #self.tableView.setObjectName(_fromUtf8("tableView"))

        #self.verticalLayout.addWidget(self.tableView)

        self.tableWidget = QtGui.QTableWidget(self.frame)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setRowCount(0)
        self.verticalLayout.addWidget(self.tableWidget)

        self.treeWidget = QtGui.QTreeWidget(self.frame)
        self.treeWidget.setObjectName(_fromUtf8("treeWidget"))
        self.treeWidget.headerItem().setText(0, _fromUtf8("1"))
        self.verticalLayout.addWidget(self.treeWidget)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.horizontalLayout.addWidget(self.frame)
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
        QtCore.QObject.connect(self.action_Open, QtCore.SIGNAL(_fromUtf8("changed()")), MainWindow.update)

        self.action_Open.triggered.connect(self.openFile)

        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('Name','Description'))
        self.tableWidget.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
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
        self.statusbar.showMessage('%d packets loaded'%len(self.data))
        self.listView.selectionModel().currentChanged.connect(self.packetSelected)
        self.tableWidget.setRowCount(0)
        self.showHeader(0)
        self.showParameter(0)
    
    def packetSelected(self, current, previous):
        row=current.row()
        self.statusbar.showMessage('Packet %d selected' % row)
        self.showHeader(row)
        self.showParameter(row)

    def showHeader(self,row):
        if not self.data:
            return
        header=self.data[row]['header']
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
        param=self.data[row]['parameter']




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

