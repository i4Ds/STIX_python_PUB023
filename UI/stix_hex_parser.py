
# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'clipboard.ui'
#
# Created by: PyQt4 UI code generator 4.12.1
#
from PyQt4 import QtCore, QtGui
import sys
from parser_ui import *


class ParserMainWindow(QtGui.QMainWindow):
    def __init__(self, ui_layout):
        QtGui.QMainWindow.__init__(self)
        self.ui = ui_layout
        ui_layout.setupUi(self)


if __name__=='__main__':
    app = QtGui.QApplication(sys.argv)
    mw=Ui_mainWindow()  
    window = ParserMainWindow(mw)
    window.show()
    sys.exit(app.exec_())

