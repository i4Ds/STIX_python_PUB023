import xmltodict
def read_xml(raw_filename):
    with open(raw_filename) as filein:
            doc = xmltodict.parse(filein.read())
            for e in doc['ns2:ResponsePart']['Response']['PktRawResponse'][
                    'PktRawResponseElement']:
                packet = {'id': e['@packetID'], 'raw': e['Packet']}
                print(packet)



read_xml('moc_test.xml')
