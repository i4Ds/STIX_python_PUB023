
## STIX raw data parser and a Qt GUI

  A python package allows parsing, browsing and analyzing STIX raw telemetry packets.  
Parsing of raw binary packets is based on IDB.  


### 1. Source code download

   Download the source code and decompress the zip file. 
 
    https://github.com/i4Ds/STIX-dataviewer/archive/master.zip


### 2. Python Environment Setup
   The packet relies on python3 and some extra python modules. 

#### 2.1 On Linux 

   - To install python3 on ubuntu/debian/Mint, run: 
```console
sudo  apt-get install python3
sudo apt install python3-pip
pip3 install numpy xmltodict PyQt5 pyqtchart scipy pymongo python-dateutil

```
   - On Redhat/Federo/CentOS/Scientific linux, run (not tested):
```console
yum install python36
yum install python3-pip
pip3 install numpy xmltodict PyQt5 pyqtchart scipy pymongo python-dateutil
```


#### 2.2 On windows

  - Download  python3.6 executable installer
 
     64-bit Windows: https://www.python.org/ftp/python/3.6.7/python-3.6.7-amd64.exe 
   
     32-bit Windows: https://www.python.org/ftp/python/3.6.7/python-3.6.7.exe 
 
  - Install python3
 
    When installing python, choose `customize installation`, 
  `install pip` and `add python path to the system environment`. 
  
  - Install dependencies

    Open Cmd as administrator and run
  ```cmd
   pip3 install numpy xmltodict PyQt5 pyqtchart scipy pymongo python-dateutil
````

### 3. How to use the package
#### 3.1. Running as a command-line parser

Usage:
python3 apps/parser.py
```console
Usage: parser.py [-h] -i [INPUT] [-o OUTPUT] [--idb IDB] [--opf {tuple,dict}]
                 [-t {binary,ascii,xml}] [--wdb] [--db-host DB_HOST]
                 [--db-port DB_PORT] [--db-user DB_USER] [--db-pwd DB_PWD]
                 [-m COMMENT] [--SPID [SPID [SPID ...]]]
                 [--services [SERVICES [SERVICES ...]]] [-v VERBOSE]
                 [-l LOGFILE]

optional arguments:
  -h, --help            show this help message and exit

Required arguments:
  -i [INPUT]            Input raw data filename.

Optional arguments:
  -o OUTPUT             Output python pickle filename.
  --idb IDB             IDB filename (sqlite3).
  --opf {tuple,dict}    format to store output parameters. 
  -t {binary,ascii,xml}
                        Input file type. Three types (binary, ascii or xml)
                        are supported. Filename extensions will be used to detect file types if not specified.
  --wdb                 Write decoded packets to local MongoDB.
  --db-host DB_HOST     MongoDB host IP.
  --db-port DB_PORT     MongoDB host port.
  --db-user DB_USER     MongoDB username.
  --db-pwd DB_PWD       MongoDB password.
  -m COMMENT            comment
  --SPID [SPID [SPID ...]]
                        Only to parse packets of the given SPIDs.
  --services [SERVICES [SERVICES ...]]
                        Only to parse packets of the given service types.
  -v VERBOSE            Logger verbose level
  -l LOGFILE, --log LOGFILE
                        Log filename
```

Example:
```console
python3 apps/parser.py -i <RAW_DATA_FILENAME> -o <OUTPUT>  -v  <Verbose level>
```

#### 3.2. Embedding the parser in your code.  
  Here are several examples.
 - Example 1

   Parsing a raw data file and dumping the packets to a python pickle file

```python
#!/usr/bin/python3 
from core import stix_parser
parser = stix_parser.StixTCTMParser()
parser.parse_file('raw.binary', 'output.pkl')
```
 - Example 2

   Parsing a raw data file and print the packets. 

```python
#!/usr/bin/python3 
from core import stix_parser

f=open('raw.binary','rb')
buffer=f.read()

parser = stix_parser.StixTCTMParser()
packets=parser.parse_binary(buffer)
for packet in packets:
  print(packet['header'])
  print(packet['parameters'])
```

 - Example 3:
```python

#!/usr/bin/python3 
import pprint
from core import stix_parser
parser = stix_parser.StixTCTMParser()
data='0d e5 c3 ce 00 1a 10 03 19 0e 80 00 87 46 6e 97 04 80 00 87 46 00 00 00 00 00 00 00 00 00 00 00 00'
packets=parser.parse_hex(data)

pprint.pprint(packets)

```

Output example:

```python
{
 'header': {'APID': 1509,
            'APID_pid': 94,
            'PUS': 16,
            'SCET': 2147518278.4319916,
            'SPID': 54103,
            'SSID': 4,
            'TMTC': 'TM',
            'TPSD': -1,
            'UTC': '2068-01-19T12:51:18.431',
            'category': 5,
            'coarse_time': 2147518278,
            'descr': 'STIX HK report - SID 4',
            'destination': 14,
            'fine_time': 28311,
            'header_flag': 1,
            'length': 17,
            'packet_id': 3557,
            'packet_type': 0,
            'process_id': 222,
            'seg_flag': 3,
            'segmentation': 'stand-alone packet',
            'seq_count': 974,
            'service_subtype': 25,
            'service_type': 3,
            'unix_time': 3094203078.4319916,
            'version': 0},
 'parameters': [('NIX00020', (4,), '', []),
                ('NIX00059', (2147518278,), '', []),
                ('NIXD0059', (0,), 'NotAvailable', []),
                ('NIXD0060', (0,), 'NoSignNThrFlux', []),
                ('NIXD0061', (0,), 'NoFlareDetect', []),
                ('NIXG0020', (0,), '', []),
                ('NIX00283', (0,), '', []),
                ('NIX00284', (0,), '', []),
                ('NIX00063', (0,), '', []),
                ('NIXD0064', (0,), 'False', []),
                ('NIXG0064', (0,), '', []),
                ('ZZPAD032', (0,), '', [])]}
```

Each parameter has a structure as follows:

 - The first column: Parameter name,  
 - The second column: raw value in a tuple. Raw parameters can be binary arrays or consist of several integers. 
 - The third column: engineering value, decompressed value, or an empty string
 - The fourth column:  an empty list, or its children if it is a repeater. 


Output parameters will be stored in python dictionaries if the following line is added:
 ```python
   parser.set_parameter_format('dict')
   ```
The output will be

```python
[{'header': {'APID': 1509,
            'APID_packet_category': 5,
            'APID_process_ID': 94,
            'DESCR': 'STIX HK report - SID 4',
            'PUS': 16,
            'SPID': 54103,
            'SSID': 4,
            'TMTC': 'TM',
            'TPSD': -1,
            'coarse_time': 2147518278,
            'destination': 14,
            'fine_time': 28311,
            'header_flag': 1,
            'length': 17,
            'packet_id': 3557,
            'packet_type': 0,
            'process_id': 222,
            'seg_flag': 3,
            'segmentation': 'stand-alone packet',
            'seq_count': 974,
            'service_subtype': 25,
            'service_type': 3,
            'time': 2147518278.4319916,
            'version': 0},
 'parameters': [{'desc': 'SID', 'name': 'NIX00020', 'raw': (4,), 'eng': ''},
                {'desc': 'Heartbeat value',
                 'name': 'NIX00059',
                 'raw': (2147518278,),
                 'eng': ''},
                {'desc': 'Flare location',
                 'name': 'NIXD0059',
                 'raw': (0,),
                 'eng': 'NotAvailable'},
                {'desc': 'Non-thermal flare index',
                 'name': 'NIXD0060',
                 'raw': (0,),
                 'eng': 'NoSignNThrFlux'},
                {'desc': 'Thermal flare index',
                 'name': 'NIXD0061',
                 'raw': (0,),
                 'eng': 'NoFlareDetect'},
                {'desc': 'Flare - global',
                 'name': 'NIXG0020',
                 'raw': (0,),
                 'eng': ''},
                {'desc': 'Flare Location Z',
                 'name': 'NIX00283',
                 'raw': (0,),
                 'eng': ''},
                {'desc': 'Flare Location Y',
                 'name': 'NIX00284',
                 'raw': (0,),
                 'eng': ''},
                {'desc': 'Flare Duration',
                 'name': 'NIX00063',
                 'raw': (0,),
                 'eng': ''},
                {'desc': 'Attenuator motion flag',
                 'name': 'NIXD0064',
                 'raw': (0,),
                 'eng': 'False'},
                {'desc': 'HK global 15',
                 'name': 'NIXG0064',
                 'raw': (0,),
                 'eng': ''}}
               ]
```

#### 3.3 Using the GUI 
##### 3.3.1 Run the GUI
- On Linux
```console
chmod +x run_gui.sh
./run_gui.sh
```
- On Windows
   Double clicking  "run_gui.bat" in the source code directory
##### 3.3.2 GUI basic functions
  The GUI allows parsing/loading and then displaying STIX packets in the following data formats/sources:
   - STIX raw data
   - SOC XML format
   - MOC ASCII format
   - packets stored in  python pickle files (pkl and pklz)
   - packets stored in NoSQL database MongoDB
   - packets received from TSC via socket
   - STIX TM binary hex string copied from the clipboard

  The GUI also allows plotting parameters as a function of timestamp or packet number. 
##### 3.3.3  GUI plugins
  One could create plugins to analyze the packets loaded in the GUI.
  The plugin manager can be loaded by clicking "Tool->Plugins" or the plugin icon in the toolbar. 
  Here is a plugin source code example
````python
#plugin example
import pprint
class Plugin:
    def __init__(self,  packets=[], current_row=0):
        self.packets=packets
        self.current_row=current_row
        print("Plugin  loaded ...")
        
    def run(self):
        # your code goes here
        print('current row')
        print(self.current_row)
        if len(self.packets)>1:
            pprint.pprint(self.packets[self.current_row])
            
````
  More plugin examples are available in  plugins/


##### 3.3.4 GUI screenshots

![GU data parser GUI](screenshots/stix_parser_1.jpg)
![GU data parser GUI](screenshots/stix_parser_2.jpg)



### 4. How to convert IDB from mdb format  to a sqlite database on Linux (Ubuntu)

- Install mdbtools and sqlite3
```sh
sudo apt-get install mdbtools sqlite3  
```

- Use the script  idb/mdb2sql.sh to convert mdb to sql
```bash
sh idb/mdb2sql.sh  STIX_IDB.mdb > idb.sql

```
- Append the following lines to the end of the generated sql file
```sh
update PCF set PCF_WIDTH=16 where PCF_NAME="NIX00123";
update PCF set PCF_WIDTH=8 where PCF_NAME="ZZPAD008";
update PCF set PCF_WIDTH=16 where PCF_NAME='ZZPAD016';
update PCF set PCF_WIDTH=24 where PCF_NAME='ZZPAD024';
update PCF set PCF_WIDTH=32 where PCF_NAME='ZZPAD032';

```

- Create IDB sqlite3 database using the sql file
```bash
sqlite3 idb.sqlite3 < idb.sql
```

One may see some errors. For example, " table  Name AutoCorrect Save Failures already exists".  
Those tables are not used by this parser. They can be removed from the sql script. 

- Copy idb.sqlite3 to idb/






