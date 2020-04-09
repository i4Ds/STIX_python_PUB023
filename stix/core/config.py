#!/usr/bin/python3
mongodb = {'host': 'localhost', 'user': '', 'password': '', 'port': 27017}
idb = {
        'filename': 'stix/data/idb/idb.sqlite',
        }
spice={
        'tls_filename':'stix/data/SPICE/kernels/lsk/naif0012.tls',
        'sclk_filename':'stix/data/SPICE/kernels/sclk/solo_ANC_soc-sclk_20200401_V01.tsc'
        }
deamon={
        #'raw_patterns':['/opt/stix/testdata/*ascii', '/home/xiaohl/data/*ascii'],
        'data_source':{
            'GU':['/opt/stix/testdata/*ascii','/home/xiaohl/FHNW/STIX/NECP/NECP_IX2/GroundTests/*ascii'],
            'PFM':[]
            },
        'log_path': '/opt/stix/log/'
        }
