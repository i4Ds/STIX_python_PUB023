#bsd data analyzer
import sys
import numpy as np
import pymongo
from pprint import pprint
from core import stix_datatypes as sdt
DATA_REQUEST_REPORT_SPIDS = [54114, 54115, 54116, 54117, 54143, 54125]

SUPPORTED_SPIDS = [54114, 54115, 54116, 54125]

DATA_REQUEST_REPORT_NAME = {
    54114: 'L0',
    54115: 'L1',
    54116: 'L2',
    54117: 'L3',
    54143: 'L4',
    54125: 'ASP'
}


class StixBulkL0Analyzer(object):
    def __init__(self):
        self.time = []
        self.rcr = []
        self.dt = []
        self.pixel_mask = []
        self.detector_mask = []
        self.triggers = []
        self.hits = []
        self.hits_time_int = np.zeros((33, 12, 32))  #total hits
        self.hits_time_ene_int = np.zeros(
            (33, 12))  # energy integrated total hits
        #self.T0=[]
        self.eacc_SKM = ()
        self.trig_SKM = ()
        self.request_id = -1
        self.packet_unix = 0

    def format_report(self):
        report = {
            'packet_unix': self.packet_unix,
            'time': self.time,
            'dt': self.dt,
            'rcr': self.rcr,
            'pixel_mask': self.pixel_mask,
            'detector_mask': self.detector_mask,
            'triggers': self.triggers,
            'hits': self.hits,  #data
            'hits_time_int': self.hits_time_int.tolist(),
            'hits_time_ene_int': self.hits_time_ene_int.tolist(),
            'status': 'OK',
        }
        return report

    def merge(self, cursor):

        for pkt in cursor:

            packet = sdt.Packet(pkt)
            self.request_id = packet[3].raw
            self.packet_unix = packet['unix_time']
            T0 = packet[12].raw
            num_structures = packet[13].raw
            self.eacc_SKM = (packet[5].raw, packet[6].raw, packet[7].raw)
            self.trig_SKM = (packet[9].raw, packet[10].raw, packet[11].raw)

            trig_idx = 1
            #uncompressed counts
            if sum(self.trig_SKM) > 0:
                trig_idx = 2

            counts_idx = 1  #raw value
            if sum(self.eacc_SKM) > 0:
                counts_idx = 2
            children = packet[13].children
            print(len(children))

            for i in range(0, num_structures):
                offset = i * 23
                self.time.append(children[offset][1] * 0.1 + T0)
                self.rcr.append(children[offset + 1][1])
                self.dt.append(children[offset + 2][1] * 0.1)
                self.pixel_mask.append(children[offset + 4][1])
                self.detector_mask.append(children[offset + 5][1])
                spectrum = np.zeros((32, 12, 32))
                self.triggers.append(
                    [children[k + 6][trig_idx] for k in range(0, 16)])
                #id 6-22, 16 trigger accumulators
                num_samples = children[22][1]
                samples = children[22][3]
                for j in range(0, num_samples):
                    k = j * 5
                    pixel = samples[k + 1][1]
                    detector = samples[k + 2][1]
                    energy_bin = samples[k + 3][1]
                    num_bits = samples[k + 4][1]
                    continous_counts = samples[k + 4][3]
                    counts = 1
                    if num_bits == 1:
                        counts = continous_counts[0][counts_idx]
                    if num_bits == 2:
                        counts = continous_counts[0][counts_idx] << 8
                        counts += continous_counts[1][counts_idx]
                    spectrum[detector][pixel][energy_bin] = counts
                    self.hits_time_int[detector][pixel][energy_bin] += counts
                    self.hits_time_ene_int[detector][pixel] += counts
                self.hits.append(spectrum.tolist())

        return self.format_report()


class StixBulkL1L2Analyzer(object):
    def __init__(self):
        self.time = []
        self.rcr = []
        self.dt = []
        self.pixel_mask = []
        self.detector_mask = []
        self.triggers = []
        self.hits = []
        self.hits_time_int = np.zeros((33, 12, 32))  #total hits
        self.hits_time_ene_int = np.zeros(
            (33, 12))  # energy integrated total hits
        #self.T0=[]
        self.eacc_SKM = ()
        self.trig_SKM = ()
        self.request_id = -1
        self.packet_unix = 0
        self.groups = []

    def format_report(self):
        report = {
            'request_id': self.request_id,
            'packet_unix': self.packet_unix,
            'eacc_SKM': self.eacc_SKM,
            'trig_SKM': self.trig_SKM,
            'groups': self.groups,
            'status': 'OK',
        }
        return report

    def merge(self, cursor):
        for pkt in cursor:
            packet = sdt.Packet(pkt)
            self.request_id = packet[3].raw
            self.packet_unix = packet['unix_time']
            T0 = packet[12].raw
            num_structures = packet[13].raw
            self.eacc_SKM = (packet[5].raw, packet[6].raw, packet[7].raw)
            self.trig_SKM = (packet[9].raw, packet[10].raw, packet[11].raw)

            trig_idx = 1
            #uncompressed counts
            if sum(self.trig_SKM) > 0:
                trig_idx = 2
            counts_idx = 1  #raw value
            if sum(self.eacc_SKM) > 0:
                counts_idx = 2
            children = packet[13].children
            group = {}
            for i in range(0, num_structures):
                offset = i * 22
                time = children[offset][1] * 0.1 + T0
                rcr = children[offset + 1][1]
                pixel_mask = [e[1] for e in children[offset + 2][3]]
                detector_mask = children[offset + 3][1]
                integrations = children[offset + 4][1]
                triggers = [children[k + 5][trig_idx] for k in range(0, 16)]
                #id 6-22, 16 trigger accumulators
                num_samples = children[21 + offset][1]
                samples = children[21 + offset][3]
                energies = []
                for j in range(0, num_samples):
                    k = j * 3
                    E1_low = samples[k + 1][1]
                    E2_high = samples[k + 2][1]
                    pixel_counts = [e[counts_idx] for e in samples[k + 3][3]]
                    energies.append([E1_low, E2_high, pixel_counts])
                group = {
                    'time': time,
                    'rcr': rcr,
                    'pixel_mask': pixel_mask,
                    'detector_mask': detector_mask,
                    'triggers': triggers,
                    'integrations': integrations,
                    'energies': energies,
                    'status': 'OK',
                }

                self.groups.append(group)
        return self.format_report()


class StixBulkAspectAnalyzer(object):
    def __init__(self):
        pass

    def merge(self, cursor):
        readouts = [[], [], [], []]
        read_time = []
        packet_utc = ''
        for pkt in cursor:
            packet = sdt.Packet(pkt)
            packet_utc = packet['UTC']
            T0 = packet[1].raw + packet[2].raw / 65536.
            dt = packet[4].raw / 64 * (1 / 64.)  #has to be fixed
            children = packet[5].children
            for i, param in enumerate(children):
                readouts[i % 4].append(param[1])
                if i % 4 == 0:
                    read_time.append(dt * int(i / 4) + T0)

        return {
            'packet_utc': packet_utc,
            'readouts': readouts,
            'read_time': read_time,
            'status': 'OK',
        }


def to_dict(db, record_id):
    collection_requests = db['data_requests']
    collection_packets = db['packets']
    if not collection_requests or not collection_packets:
        return {'status': 'DB_ERROR'}
    requests = list(collection_requests.find({'_id': record_id}).limit(1))
    if not requests:
        return {'status': 'INVALID_REQUEST_ID'}
    request = requests[0]
    SPID = request['SPID']
    if request['SPID'] not in SUPPORTED_SPIDS:
        return {'status': 'UNSUPPORTED_PACKET'}
    packet_ids = request['packet_ids']
    cursor = collection_packets.find({'_id': {'$in': packet_ids}})
    result = {'status': 'OK'}
    if SPID == 54125:
        analyzer = StixBulkAspectAnalyzer()
        result = analyzer.merge(cursor)
    elif SPID == 54114:
        analyzer = StixBulkL0Analyzer()
        result = analyzer.merge(cursor)
    else:
        analyzer = StixBulkL1L2Analyzer()
        result = analyzer.merge(cursor)
    if result:
        result['packet_ids'] = packet_ids
        result['SPID'] = SPID
    return result
