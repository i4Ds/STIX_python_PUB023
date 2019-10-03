#!/usr/bin/python3
import sys
sys.path.append('..')
sys.path.append('.')
import os
import pickle
import gzip
import numpy as np
import re
import binascii
import xmltodict
import pprint
import socket

from PyQt5 import uic, QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis, QBarSeries, QBarSet, QScatterSeries

from core import stix_parser
from core import stix_global
from core import stix_writer
from core import idb
from datetime import datetime
from UI import mainwindow_rc5
from UI import mainwindow
from UI import mongo_dialog
from UI import tsc_connection
from functools import partial
from core import mongo_db as mgdb
from core import stix_logger


class StixSocketPacketReceiver(QThread):
    """
    QThread to receive packets via socket
    """
    packetArrival = pyqtSignal(list)
    error = pyqtSignal(str)
    info = pyqtSignal(str)
    warn = pyqtSignal(str)

    def __init__(self, host, port):
        super(StixSocketPacketReceiver, self).__init__()
        self.port = port
        self.host = host
        self.stix_tctm_parser = stix_parser.StixTCTMParser()
        stix_logger._stix_logger.set_signal(self.info, self.warn, self.error)

    def run(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.host, self.port))
            self.info.emit('Receiving packets from {}:{}'.format(
                self.host, self.port))
        except Exception as e:
            self.error.emit(str(e))
            return
        try:
            buf = b''
            while True:
                data = s.recv(4096)
                if not data:
                    break
                buf += data
                if buf.endswith(b'<-->'):
                    data2 = buf.split()
                    if buf[0:9] == 'TM_PACKET'.encode():
                        data_hex = data2[-1][0:-4]
                        data_binary = binascii.unhexlify(data_hex)
                        packets = self.stix_tctm_parser.parse_binary(
                            data_binary, 0)
                        if packets:
                            packets[0]['header']['arrival'] = str(
                                datetime.now())
                            self.packetArrival.emit(packets)
                    buf = b''
        except Exception as e:
            self.error.emit(str(e))
        finally:
            s.close()


class StixFileReader(QThread):
    """
    thread
    """
    dataLoaded = pyqtSignal(list)
    error = pyqtSignal(str)
    info = pyqtSignal(str)
    warn = pyqtSignal(str)

    def __init__(self, filename):
        super(StixFileReader, self).__init__()
        self.filename = filename
        self.data = []
        self.stix_tctm_parser = stix_parser.StixTCTMParser()
        stix_logger._stix_logger.set_signal(self.info, self.warn, self.error)
    def run(self):
        self.data = []
        filename = self.filename
        if filename.endswith('.pklz'):
            self.info.emit('Loading {} ...'.format(filename))
            f = gzip.open(filename, 'rb')
            self.data = pickle.load(f)['packet']
            f.close()
        elif filename.endswith('.pkl'):
            f = open(filename, 'rb')
            self.info.emit('Loading ...')
            self.data = pickle.load(f)['packet']
            f.close()
        elif filename.endswith(('.dat', '.binary','.BDF')):
            self.parseRawFile(filename)
        # elif filename.endswith(('.db', '.sqlite')):
        #    self.readSqliteDB(filename)
        elif filename.endswith('.xml'):
            self.parseESOCXmlFile(filename)
        elif filename.endswith('.ascii'):
            self.parseMocAsciiFile(filename)
        else:
            self.error.emit('unknown file type: {}'.format(filename))
        self.dataLoaded.emit(self.data)

    def parseMocAsciiFile(self, filename):
        self.data = []
        with open(filename) as fd:
            self.info.emit('Reading packets from the file {}'.format(filename))
            idx = 0
            for line in fd:
                [utc_timestamp, data_hex] = line.strip().split()
                data_binary = binascii.unhexlify(data_hex)
                packets = self.stix_tctm_parser.parse_binary(data_binary, 0)
                if packets:
                    packets[0]['header']['utc'] = utc_timestamp
                self.data.extend(packets)
                if idx % 10 == 0:
                    self.info.emit('{} packet have been read'.format(idx))
                idx += 1

    def parseESOCXmlFile(self, in_filename):
        packets = []
        try:
            fd = open(in_filename)
        except Exception as e:
            self.error.emit('Failed to open {}'.format(str(e)))
        else:

            self.info.emit('Parsing {}'.format(in_filename))
            doc = xmltodict.parse(fd.read())
            for e in doc['ns2:ResponsePart']['Response']['PktRawResponse'][
                    'PktRawResponseElement']:
                packet = {'id': e['@packetID'], 'raw': e['Packet']}
                packets.append(packet)
        num = len(packets)
        freq = 1
        if num > 100:
            freq = num / 100

        for i, packet in enumerate(packets):
            data_hex = packet['raw']
            data_binary = binascii.unhexlify(data_hex)
            data = data_binary[76:]

            packets = self.stix_tctm_parser.parse_binary(data, 0)
            if i % freq == 0:
                self.info.emit("{:.0f}% loaded".format(100 * i / num))

            if not packets:
                continue
            self.data.extend(packets)

    def parseRawFile(self, filename):
        try:
            in_file = open(filename, 'rb')
        except Exception as e:
            self.error.emit('Failed to open {}'.format(str(e)))
        else:
            buf = in_file.read()
            size = os.stat(filename).st_size
            percent = int(size / 100)
            num_packets = 0
            total_read = 0
            total_packets = 0
            self.data = []
            last_percent = 0
            self.data = self.stix_tctm_parser.parse_binary(buf, 0)


class Ui(mainwindow.Ui_MainWindow):
    def __init__(self, MainWindow):
        super(Ui, self).setupUi(MainWindow)
        self.MainWindow = MainWindow
        self.stix_tctm_parser = stix_parser.StixTCTMParser()
        self.initialize()

    def close(self):
        self.MainWindow.close()

    def style(self):
        return self.MainWindow.style()

    def initialize(self):
        self.tabWidget.setCurrentIndex(0)
        self.actionExit.triggered.connect(self.close)
        self.action_Plot.setEnabled(False)

        self.actionNext.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_ArrowForward))
        self.actionPrevious.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_ArrowBack))
        self.action_Open.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DialogOpenButton))
        self.actionSave.setIcon(self.style().standardIcon(
            QtWidgets.QStyle.SP_DriveFDIcon))

        self.actionSave.triggered.connect(self.save)

        self.action_Open.triggered.connect(self.getOpenFilename)

        self.actionNext.triggered.connect(self.nextPacket)
        self.actionPrevious.triggered.connect(self.previousPacket)
        self.actionAbout.triggered.connect(self.about)

        self.actionPrevious.setEnabled(False)
        self.actionNext.setEnabled(False)
        self.actionSave.setEnabled(False)
        self.action_Plot.setEnabled(False)
        self.actionCopy.triggered.connect(self.onCopyTriggered)

        self.packetTreeWidget.currentItemChanged.connect(self.onPacketSelected)

        self.actionCopy.setEnabled(False)
        self.actionPaste.triggered.connect(self.onPasteTriggered)
        self.actionLog.triggered.connect(self.dockWidget.show)
        self.actionSet_IDB.triggered.connect(self.onSetIDBClicked)
        self.plotButton.clicked.connect(self.onPlotButtonClicked)
        self.exportButton.clicked.connect(self.onExportButtonClicked)
        self.action_Plot.triggered.connect(self.onPlotActionClicked)
        self.actionLoad_mongodb.triggered.connect(self.onLoadMongoDBTriggered)
        self.actionConnect_TSC.triggered.connect(self.onConnectTSCTriggered)

        self.mdb = None

        self.current_row = 0
        self.data = []
        self.x = []
        self.y = []
        self.xlabel = 'x'
        self.ylabel = 'y'

        self.buttons_enabled = False

        self.chart = QChart()
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setBackgroundRoundness(0)
        self.savePlotButton.clicked.connect(self.savePlot)

        self.chartView = QChartView(self.chart)
        self.gridLayout.addWidget(self.chartView, 1, 0, 1, 15)

        # IDB location

        self.settings = QtCore.QSettings('FHNW', 'stix_parser')
        self.idb_filename = self.settings.value('idb_filename', [], str)
        if self.idb_filename:
            idb._stix_idb = idb.IDB(self.idb_filename)
        if not idb._stix_idb.is_connected():
            self.showMessage('IDB has not been set!')
        else:
            self.showMessage('IDB found: {} '.format(
                idb._stix_idb.get_idb_filename()), 1)

    def onExportButtonClicked(self):
        if self.y:
            filename = str(
                QtWidgets.QFileDialog.getSaveFileName(None, "Save file", "",
                                                      "*.csv")[0])
            if filename:
                with open(filename, 'w') as f:
                    f.write('{},{}\n'.format(self.xlabel, self.ylabel))
                    for xx, yy in zip(self.x, self.y):
                        f.write('{},{}\n'.format(xx, yy))
                    self.showMessage(
                        'The data has been written to {}'.format(filename))
        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('Plot first!')
            msgBox.setWindowTitle("Warning")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec_()

    def savePlot(self):
        # if self.figure.get_axes():
        if self.chart:
            filename = str(
                QtWidgets.QFileDialog.getSaveFileName(None, "Save file", "",
                                                      "*.png *.jpg")[0])
            if filename:
                if not filename.endswith(('.png', '.jpg')):
                    filename += '.png'
                # self.figure.savefig(filename)
                p = self.chartView.grab()
                p.save(filename)
                self.showMessage(('Saved to %s.' % filename))

        else:
            msgBox = QtWidgets.QMessageBox()
            msgBox.setIcon(QtWidgets.QMessageBox.Information)
            msgBox.setText('No figure to save')
            msgBox.setWindowTitle("STIX raw data viewer")
            msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
            msgBox.exec_()

    def onCopyTriggered(self):
        packet_id = self.current_row
        try:
            packet = self.data[packet_id]
            ss = pprint.pformat(packet)
            cb = QtWidgets.QApplication.clipboard()
            cb.clear(mode=cb.Clipboard)
            cb.setText(ss, mode=cb.Clipboard)
            self.showMessage('The packet has been copied to clipboard!', 0)
        except Exception as e:
            self.showMessage(str(e), 0)

    def onPasteTriggered(self):
        raw_hex = QtWidgets.QApplication.clipboard().text()
        if len(raw_hex) < 16:
            self.showMessage('No data in the clipboard.')
            return
        data_hex = re.sub(r"\s+", "", raw_hex)
        try:
            data_binary = binascii.unhexlify(data_hex)
            packets = self.stix_tctm_parser.parse_binary(data_binary, 0)
            if not packets:
                return
            result = packets[0]
            header = result['header']
            parameters = result['parameters']
            num_bytes_read = len(raw_hex)
            data = [{'header': header, 'parameters': parameters}]
            self.showMessage(
                ('%d bytes read from the clipboard' % num_bytes_read))
            self.onDataReady(data)
        except Exception as e:
            self.showMessageBox(str(e), data_hex)

    def showMessageBox(self, message, content):
        msg = QtWidgets.QMessageBox()
        msg.setIcon(QtWidgets.QMessageBox.Critical)
        msg.setText("Error")
        msg.setInformativeText(message)
        msg.setWindowTitle("Error")
        msg.setDetailedText(content)
        msg.setStandardButtons(QtWidgets.QMessageBox.Ok
                               | QtWidgets.QMessageBox.Cancel)
        retval = msg.exec_()

    def showMessage(self, msg, where=0):
        if where != 1:
            self.statusbar.showMessage(msg)
        if where != 0:
            self.statusListWidget.addItem(msg)
        # if destination !=0 :
        #    self.listWidget_2.addItem(msg)

    def onSetIDBClicked(self):
        self.idb_filename = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Select file', '.', 'IDB file(*.db *.sqlite *.sqlite3)')[0]

        if not self.idb_filename:
            return

        idb._stix_idb = idb.IDB(self.idb_filename)
        if idb._stix_idb.is_connected():
            #settings = QtCore.QSettings('FHNW', 'stix_parser')
            self.settings.setValue('idb_filename', self.idb_filename)
        self.showMessage('current IDB: {} '.format(
            idb._stix_idb.get_idb_filename()), 1)

    def save(self):
        self.output_filename = str(
            QtWidgets.QFileDialog.getSaveFileName(None, "Save file", "",
                                                  ".pklz .pkl .db .sqlite")[0])

        if not self.output_filename.endswith(
                ('.pklz', '.pkl', '.db', '.sqlite')):
            msg = 'unsupported file format !'
            return
        msg = 'Writing data to file %s' % self.output_filename
        self.showMessage(msg)

        if self.output_filename.endswith(('.pklz', '.pkl')):
            stw = stix_writer.StixPickleWriter(self.output_filename)
            stw.register_run(str(self.input_filename))
            stw.write_all(self.data)
            stw.done()
        elif self.output_filename.endswith('.db'):
            stw = stix_writer.StixSqliteWriter(self.output_filename)
            stw.register_run(str(self.input_filename))
            stw.write_all(self.data)
            stw.done()

        self.showMessage(
            ('Data has been written to %s ' % self.output_filename))

    def setListViewSelected(self, row):
        #index = self.model.createIndex(row, 0);
        # if index.isValid():
        #    self.model.selectionModel().select( index, QtGui.QItemSelectionModel.Select)
        pass

    def about(self):
        msgBox = QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText("STIX raw data parser and viewer, hualin.xiao@fhnw.ch")
        msgBox.setWindowTitle("Stix data viewer")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok)
        msgBox.exec_()

    def nextPacket(self):
        self.current_row += 1
        length = len(self.data)

        if self.current_row >= length:
            self.current_row = length - 1
            self.showMessage('No more packet!')

        self.showPacket(self.current_row)
        self.setListViewSelected(self.current_row)

    def previousPacket(self):
        self.current_row -= 1
        if self.current_row < 0:
            self.current_row = 0
            self.showMessage('Reach the first packet!')

        self.showPacket(self.current_row)
        self.setListViewSelected(self.current_row)

    def getOpenFilename(self):
        self.input_filename = QtWidgets.QFileDialog.getOpenFileName(
            None, 'Select file', '.',
            'STIX data file (* *.dat *.pkl *.pklz *xml *.db)')[0]
        if not self.input_filename:
            return
        self.openFile(self.input_filename)

    def openFile(self, filename):
        msg = 'Loading file %s ...' % filename
        self.showMessage(msg)
        self.dataReader = StixFileReader(filename)
        self.dataReader.dataLoaded.connect(self.onDataReady)
        self.dataReader.error.connect(self.onDataReaderError)
        self.dataReader.info.connect(self.onDataReaderInfo)
        self.dataReader.warn.connect(self.onDataReaderWarn)
        self.dataReader.start()

    def onDataReaderInfo(self, msg):
        self.showMessage(msg, 0)

    def onDataReaderWarn(self, msg):
        self.showMessage(msg, 1)

    def onDataReaderError(self, msg):
        self.showMessage(msg, 1)

    def onDataReady(self, data, clear=True, show_stat=True):
        if not clear:
            self.data.extend(data)
        else:
            self.data = data
        if data:
            self.addPacketsToView(data, clear=clear, show_stat=show_stat)
            self.enableButtons()

    def enableButtons(self):
        if not self.buttons_enabled:
            self.actionPrevious.setEnabled(True)
            self.actionNext.setEnabled(True)
            self.actionSave.setEnabled(True)
            self.actionCopy.setEnabled(True)
            self.action_Plot.setEnabled(True)
            self.buttons_enabled = True

    def addPacketsToView(self, data, clear=True, show_stat=True):
        if clear:
            self.packetTreeWidget.clear()
        #t0 = 0
        for p in data:
            if type(p) is not dict:
                continue
            header = p['header']
            root = QtWidgets.QTreeWidgetItem(self.packetTreeWidget)
            # if t0 == 0:
            #    t0 = header['time']
            timestamp_str = ''
            try:
                timestamp_str = header['utc']
            except KeyError:
                timestamp_str = '{:.2f}'.format(header['time'])
                #- t0)

            root.setText(0, timestamp_str)
            root.setText(1, '{}({},{}) - {}'.format(
                header['TMTC'], header['service_type'],
                header['service_subtype'], header['DESCR']))

        if show_stat:
            total_packets = len(self.data)
            self.showMessage(('Total packet(s): %d' % total_packets))

    def onConnectTSCTriggered(self):
        diag = QtWidgets.QDialog()
        diag_ui = tsc_connection.Ui_Dialog()
        diag_ui.setupUi(diag)
        self.tsc_host = self.settings.value('tsc_host', [], str)
        self.tsc_port = self.settings.value('tsc_port', [], str)
        if self.tsc_host:
            diag_ui.serverLineEdit.setText(self.tsc_host)
        if self.tsc_port:
            diag_ui.portLineEdit.setText(self.tsc_port)
        diag_ui.buttonBox.accepted.connect(
            partial(self.connectToTSC, diag_ui))
        diag.exec_()

    def connectToTSC(self, dui):
        host = dui.serverLineEdit.text()
        port = dui.portLineEdit.text()
        self.showMessage('Connecting to TSC...')

        self.socketPacketReceiver = StixSocketPacketReceiver(host, int(port))
        self.socketPacketReceiver.packetArrival.connect(self.onPacketArrival)
        self.socketPacketReceiver.error.connect(self.onDataReaderError)
        self.socketPacketReceiver.info.connect(self.onDataReaderInfo)
        self.socketPacketReceiver.warn.connect(self.onDataReaderWarn)
        self.socketPacketReceiver.start()

    def onPacketArrival(self, packets):
        if packets:
            self.onDataReady(packets, clear=False, show_stat=True)

    def onLoadMongoDBTriggered(self):
        diag = QtWidgets.QDialog()
        diag_ui = mongo_dialog.Ui_Dialog()
        diag_ui.setupUi(diag)
        #self.settings = QtCore.QSettings('FHNW', 'stix_parser')
        self.mongo_server = self.settings.value('mongo_server', [], str)
        self.mongo_port = self.settings.value('mongo_port', [], str)

        self.mongo_user = self.settings.value('mongo_user', [], str)
        self.mongo_pwd = self.settings.value('mongo_pwd', [], str)

        if self.mongo_server:
            diag_ui.serverLineEdit.setText(self.mongo_server)
        if self.mongo_port:
            diag_ui.portLineEdit.setText(self.mongo_port)

        if self.mongo_user:
            diag_ui.userLineEdit.setText(self.mongo_user)
        if self.mongo_pwd:
            diag_ui.pwdLineEdit.setText(self.mongo_pwd)

        diag_ui.pushButton.clicked.connect(
            partial(self.loadRunsFromMongoDB, diag_ui))
        diag_ui.buttonBox.accepted.connect(
            partial(self.loadDataFromMongoDB, diag_ui, diag))
        diag.exec_()

    def loadRunsFromMongoDB(self, dui):
        server = dui.serverLineEdit.text()
        port = dui.portLineEdit.text()
        user = dui.userLineEdit.text()
        pwd = dui.pwdLineEdit.text()

        self.showMessage('saving setting...')
        if self.mongo_server != server:
            self.settings.setValue('mongo_server', server)
        if self.mongo_port != port:
            self.settings.setValue('mongo_port', port)

        if self.mongo_user != user:
            self.settings.setValue('mongo_user', user)
        if self.mongo_pwd != pwd:
            self.settings.setValue('mongo_pwd', pwd)

        self.showMessage('connecting Mongo database ...')
        self.mdb = mgdb.MongoDB(server, int(port), user, pwd)
        if not self.mdb.is_connected():
            return

        dui.treeWidget.clear()
        self.showMessage('Fetching data...')
        for run in self.mdb.get_runs():
            root = QtWidgets.QTreeWidgetItem(dui.treeWidget)
            root.setText(0, str(run['_id']))
            root.setText(1, run['filename'])
            root.setText(2, run['date'])
            root.setText(3, str(run['start']))
            root.setText(4, str(run['end']))
        self.showMessage('Data loaded!')

    def loadDataFromMongoDB(self, dui, diag):
        selected_runs = []
        for item in dui.treeWidget.selectedItems():
            selected_runs.append(item.text(0))
        if not selected_runs:
            self.showMessage('Run not selected!')
        if selected_runs:
            diag.done(0)
            self.showMessage('Loading data ...!')
            data = self.mdb.get_packets(selected_runs[0])
            if data:
                self.onDataReady(data, clear=True)
            else:
                self.showMessage('No packets found!')
        # close

    def onPacketSelected(self, cur, pre):
        self.current_row = self.packetTreeWidget.currentIndex().row()
        self.showMessage(('Packet #%d selected' % self.current_row))
        self.showPacket(self.current_row)

    def showPacket(self, row):
        if not self.data:
            return
        header = self.data[row]['header']
        total_packets = len(self.data)
        self.showMessage(('Packet %d / %d  %s ' % (row, total_packets,
                                                   header['DESCR'])))
        self.paramTreeWidget.clear()
        header_root = QtWidgets.QTreeWidgetItem(self.paramTreeWidget)
        header_root.setText(0, "Header")
        rows = len(header)
        for key, val in header.items():
            root = QtWidgets.QTreeWidgetItem(header_root)
            root.setText(0, key)
            root.setText(1, str(val))

        params = self.data[row]['parameters']
        param_root = QtWidgets.QTreeWidgetItem(self.paramTreeWidget)
        param_root.setText(0, "Parameters")
        self.showParameterTree(params, param_root)
        self.paramTreeWidget.expandItem(param_root)
        self.paramTreeWidget.expandItem(header_root)
        self.current_row = row

    def showParameterTree(self, params, parent):
        if not params:
            return
        for p in params:
            root = QtWidgets.QTreeWidgetItem(parent)
            if not p:
                continue
            try:
                param_name = p['name']
                desc = idb._stix_idb.get_PCF_description(param_name)
                scos_desc = idb._stix_idb.get_scos_description(param_name)
                root.setToolTip(1, scos_desc)
                root.setText(0, param_name)
                root.setText(1, desc)
                root.setText(2, str(p['raw']))
                try:
                    root.setToolTip(2, hex(p['raw'][0]))
                except:
                    pass
                root.setText(3, str(p['value']))
                if 'children' in p:
                    if p['children']:
                        self.showParameterTree(p['children'], root)
            except KeyError:
                self.showMessage(
                    '[Error  ]: keyError occurred when adding parameter')
        self.paramTreeWidget.itemDoubleClicked.connect(self.onTreeItemClicked)

    def walk(self, name, params, header, ret_x, ret_y, xaxis=0, data_type=0):
        if not params:
            return
        timestamp = header['time']
        #parameters=[p for p in params if p['name'] == name]
        for p in params:
            if type(p) is not dict:
                continue
        # for p in parameters:
            if name == p['name']:
                values = None
                #print('data type:{}'.format(data_type))
                if data_type == 0:
                    values = p['raw']
                else:
                    values = p['value']
                try:
                    yvalue = None
                    if (type(values) is tuple) or (type(values) is list):
                        yvalue = float(values[0])
                    else:
                        yvalue = float(values)
                    ret_y.append(yvalue)
                    if xaxis == 1:
                        ret_x.append(timestamp)
                    else:
                        self.showMessage(('Can not plot %s  ' % str(yvalue)))
                except Exception as e:
                    self.showMessage(('%s ' % str(e)))

            if 'children' in p:
                if p['children']:
                    self.walk(name, p['children'], header, ret_x, ret_y, xaxis,
                              data_type)

    def onPlotButtonClicked(self):
        if self.chart:
            self.chart.removeAllSeries()
        if not self.data:
            return
        self.showMessage('Preparing plot ...')
        name = self.paramNameEdit.text()
        packet_selection = self.comboBox.currentIndex()
        xaxis_type = self.xaxisComboBox.currentIndex()
        data_type = self.dataTypeComboBox.currentIndex()

        timestamp = []
        self.y = []
        packet_id = self.current_row
        params = self.data[packet_id]['parameters']
        header = self.data[packet_id]['header']
        current_spid = header['SPID']
        if packet_selection == 0:
            self.walk(name, params, header, timestamp, self.y, xaxis_type,
                      data_type)
        elif packet_selection == 1:
            for packet in self.data:
                header = packet['header']
                if packet['header']['SPID'] != current_spid:
                    continue
                # only look for parameters in the packets of the same type
                params = packet['parameters']
                self.walk(name, params, header, timestamp, self.y, xaxis_type,
                          data_type)

        self.x = []

        if not self.y:
            self.showMessage('No data points')
        elif self.y:
            style = self.styleEdit.text()
            if not style:
                style = '-'
            title = '%s' % str(name)
            desc = self.descLabel.text()
            if desc:
                title += '- %s' % desc

            self.chart.setTitle(title)

            ylabel = 'Raw value'
            xlabel = name
            if data_type == 1:
                ylabel = 'Engineering  value'
            if xaxis_type == 0:
                if packet_selection == 1:
                    xlabel = "Packet #"
                else:
                    xlabel = "Repeat #"
                self.x = range(0, len(self.y))
            if xaxis_type == 1:
                self.x = [t - timestamp[0] for t in timestamp]
                xlabel = 'Time -T0 (s)'

            if xaxis_type != 2:
                series = QLineSeries()
                series2 = None
                for xx, yy in zip(self.x, self.y):
                    series.append(xx, yy)
                if 'o' in style:
                    series2 = QScatterSeries()
                    for xx, yy in zip(self.x, self.y):
                        series2.append(xx, yy)
                    self.chart.addSeries(series2)
                self.chart.addSeries(series)
                axisX = QValueAxis()
                axisX.setTitleText(xlabel)
                axisY = QValueAxis()
                axisY.setTitleText(ylabel)

                self.chart.setAxisX(axisX)
                self.chart.setAxisY(axisY)
                series.attachAxis(axisX)
                series.attachAxis(axisY)
            else:
                nbins = len(set(self.y))
                ycounts, xedges = np.histogram(self.y, bins=nbins)
                series = QLineSeries()
                for i in range(0, nbins):
                    meanx = (xedges[i] + xedges[i + 1]) / 2.
                    series.append(meanx, ycounts[i])
                self.chart.addSeries(series)
                axisX = QValueAxis()
                axisX.setTitleText(name)
                axisY = QValueAxis()
                axisY.setTitleText("Counts")

                self.chart.setAxisY(axisY)
                self.chart.setAxisX(axisX)
                series.attachAxis(axisX)
                series.attachAxis(axisY)

            self.xlabel = xlabel
            self.ylabel = ylabel
            self.chartView.setRubberBand(QChartView.RectangleRubberBand)
            self.chartView.setRenderHint(QtGui.QPainter.Antialiasing)

            msg = 'Y length: {}, min-Y:  {}, max-Y: {}'.format(
                len(self.y), min(self.y), max(self.y))

            self.showMessage(msg, 1)

            self.showMessage('The canvas updated!')

    def plotParameter(self, name=None, desc=None):
        self.tabWidget.setCurrentIndex(1)
        if name:
            self.paramNameEdit.setText(name)
        if desc:
            self.descLabel.setText(desc)
    def onPlotActionClicked(self):
        self.tabWidget.setCurrentIndex(1)
        self.plotParameter()
    def onTreeItemClicked(self, it, col):
        self.plotParameter(it.text(0), it.text(1))

if __name__ == '__main__':
    filename = None
    if len(sys.argv) >= 2:
        filename = sys.argv[1]
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    window = Ui(MainWindow)
    MainWindow.show()
    if filename:
        window.openFile(filename)
    sys.exit(app.exec_())
