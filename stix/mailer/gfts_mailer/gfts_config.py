Receivers=['hualin.xiao@fhnw.ch', 'laszlo.etesi@fhnw.ch', 'shane.maloney@tcd.ie','ghurford@ssl.berkeley.edu','stefan.koegl@fhnw.ch', 'krucker@ssl.berkeley.edu']
config={
'SqlDatabaseFileName':'/opt/gfts/db/gfts.sqlite',
'Email_from':'stix_obs@fhnw.ch',
'Email_user':'',
'Email_pwd':'',
'Email_server':'lmailer.fhnw.ch',
'logger':'/var/tmp/gfts.log',
'port':465,
'ScanDirectories': [ {'type':'from_soc', 'dir': '/home/solsoc/from_soc'},
    {'type':'transferred', 'dir': '/home/solsoc/transferred'},
    {'type':'moc', 'dir': '/home/solmoc'}
    ],
'Email_receivers':Receivers
}
