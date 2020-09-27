#!/usr/bin/python3
mongodb = {'host': 'localhost', 'user': '', 'password': '', 'port': 27017}
idb = {
    'filename': 'stix/data/idb/idb.sqlite',
}
spice_data_pattern= [
    'stix/data/SPICE/kernels/lsk/naif0012.tls',
    'stix/data/SPICE/kernels/sclk/solo_ANC_soc-sclk_*.tsc'
]
daemon = {
    #'raw_patterns':['/opt/stix/testdata/*ascii', '/home/xiaohl/data/*ascii'],
    'data_source': {
        'GU': ['/home/xiaohl/data/*.ascii'],
        'PFM': [
            '/data/*ascii', '/data/*xml',
            '/opt/stix/gfts/solmoc/from_moc/*.xml',
            '/opt/stix/gfts/solmoc/from_moc/*ascii'
        ]
    },
    'log_path': '/opt/stix/log/',
    'alert_log': '/opt/stix/log/stix_alerts.log',
    'fits_path': '/opt/stix/fits',
}

calibration = {'report_path': '/data/'}
