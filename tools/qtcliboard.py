import sys
from PyQt5.Qt import QApplication, QClipboard
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import binascii
import re
from core import stix_telemetry_parser as parser
from cBytesIO import BytesIO
def parser_clipboard_data(raw_hex):
    data_hex= re.sub(r"\s+", "", raw_hex)
    print(data_hex)
    try:
        data_binary = binascii.unhexlify(data_hex)
        in_file=BytesIO(data_binary)
        status, header, parameters, param_type, param_desc, num_bytes_read = parser.parse_one_packet(
            in_file, None)
        if header or parameters:
            return header,parameters
        else:
            return None, None
    except TypeError:
        return None, ('Non hexadecimal digit found in the clipboard')

class ExampleWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        #self.setMinimumSize(QSize(840, 640))    
        self.setGeometry(100,100,1030,800)
        self.setWindowTitle("Clipboard data parser") 
        self.button = QPushButton('Update', self)
        self.button.clicked.connect(self.handleButton)
        #self.button.setGeometry(610,820,630,830)
        # Add text field
        self.textEdit = QTextEdit()
        self.setCentralWidget(self.textEdit)
        self.layout=QVBoxLayout()
        self.layout.addWidget(self.textEdit)
        self.layout.addWidget(self.button)

    # Get the system clipboard contents
    def handleButton(self):
        self.textEdit.clear()
        text = QApplication.clipboard().text()
        header, parameter=parser_clipboard_data(text)
        self.textEdit.append(str(header))
        self.textEdit.append(str(parameter))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = ExampleWindow()
    mainWin.show()
    sys.exit( app.exec_() )
