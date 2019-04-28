from PyQt5 import uic, QtWidgets, QtCore, QtGui
import sys
import cPickle
import gzip
from core import stix_telemetry_parser 
from core import stix_global
from stix_io import stix_writer
import os
import viewer_rc5


class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UI/parser_gui/viewer.ui', self)

        self.actionExit.triggered.connect(self.close)
        #self.initialize()
        self.action_Plot.setEnabled(False)

        self.initialize()


    def initialize(self):
        self.actionNext.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowForward))
        self.actionPrevious.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_ArrowBack))
        self.action_Open.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DialogOpenButton))
        self.actionSave.setIcon(self.style().standardIcon(QtWidgets.QStyle.SP_DriveFDIcon))

        self.actionSave.triggered.connect(self.save)


        self.action_Open.triggered.connect(self.getOpenFilename)
        self.tableWidget.setColumnCount(2)
        self.tableWidget.setHorizontalHeaderLabels(('Name','Description'))
        #self.tableWidget.horizontalHeader().setResizeMode(QtWidgets.QHeaderView.Stretch)

        self.tree_header=QtWidgets.QTreeWidgetItem(['Name','description','raw','Eng value'])
        self.treeWidget.setHeaderItem(self.tree_header)
        self.actionNext.triggered.connect(self.next)
        self.actionPrevious.triggered.connect(self.previous)
        self.actionAbout.triggered.connect(self.about)
        
        self.actionPrevious.setEnabled(False)
        self.actionNext.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.action_Plot.setEnabled(False)
        self.actionLog.triggered.connect(self.dockWidget.show)
        self.actionSet_IDB.triggered.connect(self.onSetIDBClicked)
    def onSetIDBClicked(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        path = os.path.dirname(os.path.realpath(__file__))
        msgBox.setText("Please copy file idb.sqlite to the folder %s/idb/ to change IDB !"%path)
        msgBox.setWindowTitle("STIX DATA VIEWER")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()


    def save(self):
        self.output_filename = str(QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", ".pklz"))[0]
        
        if not self.output_filename:
            return

        self.statusbar.showMessage('writing to file %s'%self.output_filename)
        stw=stix_writer.stix_writer(self.output_filename)
        stw.register_run(str(self.input_filename))
        stw.write_all(self.data)
        stw.done()
        self.statusbar.showMessage('data has written to %s ' %self.output_filename)
        
    def setListViewSelected(self,row):
        #index = self.model.createIndex(row, 0);
        #if index.isValid():
        #    self.model.selectionModel().select( index, QtGui.QItemSelectionModel.Select) 
        pass

    def about(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText("STIX STIX data viewer, hualin.xiao@fhnw.ch")
        msgBox.setWindowTitle("Stix data viewer")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()

    def addLogEntry(self,msg):
        self.listWidget.addItem(msg)

    def next(self):
        self.current_row+=1
        self.showPacket(self.current_row)
        self.setListViewSelected(self.current_row)
    def previous(self):
        self.current_row-=1
        self.showPacket(self.current_row)
        self.setListViewSelected(self.current_row)

    def getOpenFilename(self):
        self.input_filename = QtWidgets.QFileDialog.getOpenFileName(None,'Select file', '.', 'STIX data file (*.dat *.pkl *.pklz)')[0]
        self.openFile(self.input_filename)

    def openFile(self,filename):
        self.data=[]
        print(filename)
        self.statusbar.showMessage('Opening file %s'%filename)
        self.addLogEntry('Opening file %s'%filename)
        if '.pkl' in filename or '.pklz' in filename:
            f=gzip.open(filename,'rb')
            self.addLogEntry('File uncompressed ...')
            self.data=cPickle.load(f)['packet']
            self.addLogEntry('Data loaded')
            f.close()
            self.displayPackets()
        elif '.dat' in filename:
            self.parseRawFile(filename)

        if self.data:
            self.actionPrevious.setEnabled(True)
            self.actionNext.setEnabled(True)
            self.actionSave.setEnabled(True)
            self.action_Plot.setEnabled(True)

    def parseRawFile(self,filename):
        self.addLogEntry('Parsing file %s'%filename)
        with open(filename, 'rb') as in_file:
            num_packets = 0
            num_fix_packets=0
            num_variable_packets=0
            num_bytes_read = 0
            stix_writer=None
            #st_writer.register_run(in_filename)
            total_packets=0
            self.data=[]
            selected_spid=0

            while True:
                status, header, parameters, param_type, param_desc, num_bytes_read = stix_telemetry_parser.parse_one_packet(in_file, 
                        self,selected_spid, output_param_type='tree')
                total_packets += 1
                if status == stix_global.NEXT_PACKET:
                    continue
                if status == stix_global.EOF:
                    break

                self.data.append({'header':header,'parameter':parameters})

            self.addLogEntry('%d packets loaded'%total_packets)

        self.displayPackets()





    def displayPackets(self):
        self.model = QtGui.QStandardItemModel()
        for p in self.data:
            header=p['header']
            msg='TM(%d,%d) - %s'%(header['service_type'],header['service_subtype'],header['DESCR'])
            self.model.appendRow(QtGui.QStandardItem(msg))
        self.listView.setModel(self.model)
        self.total_packets=len(self.data)
        self.statusbar.showMessage('%d packets loaded'%(self.total_packets))
        self.addLogEntry('%d packets loaded'%(self.total_packets))
        self.listView.selectionModel().currentChanged.connect(self.onPacketSelected)
        self.tableWidget.setRowCount(0)
        self.showHeader(0)
        self.showParameter(0)
    
    def onPacketSelected(self, current, previous):
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
            self.tableWidget.setItem(i,0,QtWidgets.QTableWidgetItem(key))
            self.tableWidget.setItem(i,1,QtWidgets.QTableWidgetItem(str(val)))
            i += 1

    def showParameter(self,row):
        if not self.data:
            return
        params=self.data[row]['parameter']
        self.treeWidget.clear()
        self.showParameterTree(params,self.treeWidget)

    def showParameterTree(self, params, parent):
        for p in  params:
            root=QtWidgets.QTreeWidgetItem(parent)
            try:
                root.setText(0,p['name'])
                root.setText(1,p['descr'])
                root.setText(2,str(p['raw']))
                root.setText(3,str(p['value']))
                if 'child' in p:
                    if p['child']:
                        self.showParameterTree(p['child'],root)
            except KeyError:
                self.addLogEntry('[Error  ]: keyError adding parameter')
        self.treeWidget.itemDoubleClicked.connect(self.onTreeItemClicked)

    def onTreeItemClicked(self, it, col):
        print(it, col, it.text(0))


    def error(self,  msg, description=''):
        if description:
            self.addLogEntry('[ERROR  ] {0}: {1}'.format(msg, description))
        else:
            self.addLogEntry('[ERROR  ] : {}'.format(msg))

    def warning(self, msg, description=''):
        if description:
            self.addLogEntry('[WARNING] {0}: {1}'.format(msg, description))
        else:
            self.addLogEntry('[WARNING] : {}'.format(msg))

    def info(self,  msg, description=''):
        if description:
            self.addLogEntry('[INFO   ] {0}: {1}'.format(msg, description))
        else:
            self.addLogEntry('[INFO   ] : {}'.format(msg))                





if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    sys.exit(app.exec_())
