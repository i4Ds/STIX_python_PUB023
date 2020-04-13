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
        'data_source':{
            'GU':['/opt/stix/testdata/*ascii'],
            'PFM':['/opt/stix/gfts/solmoc/from_moc/*Raw*xml', '/opt/stix/gfts/solmoc/from_moc/*ascii' ]
            },
        'log_path': '/opt/stix/log/'
        }
