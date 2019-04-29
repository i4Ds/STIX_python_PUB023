from PyQt5 import uic, QtWidgets, QtCore, QtGui
import sys
import pickle
import gzip
from core import stix_telemetry_parser 
from core import stix_global
from stix_io import stix_writer
import os
from UI import mainwindow_rc5
from UI.mainwindow import Ui_MainWindow

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
from PyQt5.QtCore import QThread, pyqtSignal
import re
import binascii
from io import StringIO

class StixDataReader(QThread):
    """
    thread
    """
    dataLoaded= pyqtSignal(list)
    def __init__(self,filename):
        super(StixDataReader,self).__init__()
        self.filename=filename
        self.data=[]

    def run(self):
        self.data=[]
        filename=self.filename
        if '.pkl' in filename or '.pklz' in filename:
            f=gzip.open(filename,'rb')
            self.data=pickle.load(f)['packet']
            f.close()
        elif '.dat' in filename:
            self.parseRawFile()
        self.dataLoaded.emit(self.data)

    def parseRawFile(self):
        filename=self.filename
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
                        None,selected_spid, output_param_type='tree')
                total_packets += 1
                if status == stix_global.NEXT_PACKET:
                    continue
                if status == stix_global.EOF:
                    break
                self.data.append({'header':header,'parameter':parameters})





class Ui(QtWidgets.QMainWindow):
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('UI/mainwindow.ui', self)


        self.initialize()


    def initialize(self):
        self.tabWidget.setCurrentIndex(0)
        self.actionExit.triggered.connect(self.close)
        self.action_Plot.setEnabled(False)

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
        self.actionNext.triggered.connect(self.nextPacket)
        self.actionPrevious.triggered.connect(self.previousPacket)
        self.actionAbout.triggered.connect(self.about)
        
        self.actionPrevious.setEnabled(False)
        self.actionNext.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.action_Plot.setEnabled(False)
        self.actionLog.triggered.connect(self.dockWidget_2.show)
        self.actionSet_IDB.triggered.connect(self.onSetIDBClicked)

        self.plotButton.clicked.connect(self.onPlotButtonClicked)
        self.action_Plot.triggered.connect(self.onPlotActionClicked)

        self.current_row=0

        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        self.gridLayout.addWidget(self.canvas, 1, 0, 1, 13)
        self.savePlotButton.clicked.connect(self.savePlot)
        self.actionPaste.triggered.connect(self.paste)
        
    def savePlot(self):
        if self.figure.get_axes():
            filename= str(QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", "*.pdf *.png *.svg *.jpg")[0])
            if filename:
                self.figure.savefig(filename)
                self.statusbar.showMessage('Saved to %s.'%filename)
        

        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('The canvas is empty!')
            msgBox.setWindowTitle("STIX DATA VIEWER")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec_()



    def paste(self):
        raw_hex= QtWidgets.QApplication.clipboard().text()
        data_hex= re.sub(r"\s+", "", raw_hex)
        if not data_hex:
            self.statusbar.showMessage('No data in the clipboard.')
            return
        try:
            data_binary = binascii.unhexlify(data_hex)
            in_file=StringIO(data_binary)
            status, header, parameters, param_type, param_desc, num_bytes_read = stix_telemetry_parser.parse_one_packet(
                in_file, self)
            data=[{'header':header,'parameter':parameters}]
            self.addLogEntry('%d bytes read from the clipboard'%num_bytes_read)
            self.onDataLoaded(data)
        except TypeError:
            self.statusbar.showMessage('Failed to parse the packet')






    def onSetIDBClicked(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        path = os.path.dirname(os.path.realpath(__file__))
        msgBox.setText("Please copy file idb.sqlite to the folder %s/idb/ to change IDB !"%path)
        msgBox.setWindowTitle("STIX DATA VIEWER")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()


    def save(self):
        self.output_filename = str(QtWidgets.QFileDialog.getSaveFileName(self, "Save file", "", ".pklz")[0])
        
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
        self.listWidget_2.addItem(msg)

    def nextPacket(self):
        self.current_row+=1
        self.showPacket(self.current_row)
        self.setListViewSelected(self.current_row)
    def previousPacket(self):
        self.current_row-=1
        self.showPacket(self.current_row)
        self.setListViewSelected(self.current_row)

    def getOpenFilename(self):
        self.input_filename = QtWidgets.QFileDialog.getOpenFileName(None,'Select file', '.', 'STIX data file (*.dat *.pkl *.pklz)')[0]
        if not self.input_filename:
            return
        self.openFile(self.input_filename)

    def openFile(self,filename):
        self.statusbar.showMessage('Opening file %s'%filename)
        self.addLogEntry('Loading file %s ...'%filename)

        self.dataReader=StixDataReader(filename)
        self.dataReader.dataLoaded.connect(self.onDataLoaded)
        self.dataReader.start()


    def onDataLoaded(self,data):
        self.data=data
        total_packets=len(self.data)
        self.statusbar.showMessage('%d packets loaded'%total_packets)

        self.displayPackets()
        if self.data:
            self.actionPrevious.setEnabled(True)
            self.actionNext.setEnabled(True)
            self.actionSave.setEnabled(True)
            self.action_Plot.setEnabled(True)

        self.addLogEntry('%d packets loaded'%total_packets)






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
            if not p:
                continue
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

    def walk_tree(self,name, params, header, ret_x, ret_y,xaxis=0):
        if not params:
            return
        timestamp=header['time']
        for p in  params:
            if not p:
                continue
            if name == p['name']:
                try:
                    ret_y.append(float(p['raw'][0]))
                    if xaxis==1:
                        ret_x.append(timestamp)
                except:
                    self.addLogEntry('Parameter %s ignored'%str(p))
            if 'child' in p:
                if p['child']:
                    self.walk_tree(name, p['child'], header, ret_x, ret_y, xaxis)



    def onPlotButtonClicked(self):
        if not self.data:
            return 
        name=self.paramNameEdit.text()
        packet_selection=self.comboBox.currentIndex()
        xaxis_type=self.xaxisComboBox.currentIndex()




        timestamp=[]
        y=[]
        if packet_selection==0:
            packet_id=self.current_row
            params=self.data[packet_id]['parameter']
            header=self.data[packet_id]['header']
            self.walk_tree(name, params,header,timestamp,y, xaxis_type)
        elif packet_selection==1:
            for packet in self.data:
                params=packet['parameter']
                header=packet['header']
                self.walk_tree(name, params,header,timestamp,y,xaxis_type)

        ax=self.figure.add_subplot(111)
        ax.clear()
        if not y:
            self.statusbar.showMessage('No data points')
        elif y:
            style=self.styleEdit.text()
            if not style:
                style='o-'

            title='%s'%str(name)
            desc=self.descLabel.text()
            if desc:
                title += '- %s'%desc

            if xaxis_type ==0:
                ax.plot(y,style)
                ax.set_xlabel("Packet #")
                ax.set_ylabel("Raw value")
            elif xaxis_type==1:
                x=[t-timestamp[0] for t in timestamp]
                ax.plot(x,y,style)
                ax.set_xlabel("Time - T0 (s)")
                ax.set_ylabel("Raw value")
            else:
                #histogram
                nbins=len(set(y))
                ax.hist(y,nbins, density=True, facecolor='g', alpha=0.75)
                ax.set_xlabel("%s"%title)
                ax.set_ylabel("Counts")



            ax.set_title(title)

            self.canvas.draw()
            self.statusbar.showMessage('The canvas updated!')
            




    def plotParameter(self,name=None, desc=None):
        self.tabWidget.setCurrentIndex(1)
        if name:
            self.paramNameEdit.setText(name)
        if desc:
            self.descLabel.setText(desc)

    def onPlotActionClicked(self):
        self.tabWidget.setCurrentIndex(1)
        self.plotParameter()


    def onTreeItemClicked(self, it, col):
        #print(it, col, it.text(0))
        self.plotParameter(it.text(0),it.text(1))



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
    filename=None
    if len(sys.argv)>=2:
        filename=sys.argv[1]

    app = QtWidgets.QApplication(sys.argv)
    window = Ui()
    window.show()
    if filename:
        window.openFile(filename)
    sys.exit(app.exec_())
