"""
STIX science data products
"""
import numpy as np
from datetime import timedelta
from math import modf

from stix.core.stix_datetime import scet_to_datetime
from stix.fits.io.science import xray_l0_fits


class XrayL0:
    """
    X-ray Level 0 data
    """
    def __init__(self, stix_packets):

        # Control
        self.tc_packet_id_ref = stix_packets.get('NIX00001')[0]
        self.tc_packet_seq_control = stix_packets.get('NIX00002')[0]
        self.request_id = stix_packets.get('NIX00037')[0]
        self.compression_scheme_counts = (stix_packets['NIXD0007'][0],
                                          stix_packets['NIXD0008'][0],
                                          stix_packets['NIXD0009'][0])
        self.compression_scheme_trig = (stix_packets['NIXD0010'][0],
                                        stix_packets['NIXD0011'][0],
                                        stix_packets['NIXD0011'][0])
        self.time_stamp = stix_packets.get('NIX00402')[0]
        self.num_structures = stix_packets.get('NIX00403')[0]
        self.start_time = stix_packets.get('NIX00404')[0]
        self.rcr = stix_packets.get('NIX00401')[0]
        self.integration_duration = stix_packets.get('NIX00405')[0]
        self.pixel_mask = stix_packets.get('NIXD0407')[0]
        self.detector_mask = stix_packets.get('NIXD0407')[0]
        for i, num in enumerate(range(408, 424)):
            setattr(self, f'triggers_{i}', stix_packets.get(f'NIX00{num}')[0])

        # TODO seems off
        fine, coarse = modf(self.time_stamp)
        self.scet_coarse = int(coarse)
        self.scet_fine = int(fine * 2**16)

        self.obs_utc = scet_to_datetime(f'{self.scet_coarse}:{self.scet_fine}')
        self.obs_beg = self.obs_utc
        self.obs_end = self.obs_beg + timedelta(seconds=self.integration_duration * 0.1)
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        # Data
        self.num_samples = stix_packets.get('NIX00406')[0]
        self.pixel_id = stix_packets.get('NIXD0158')
        self.detector_id = stix_packets.get('NIXD0153')
        self.channel = stix_packets.get('NIXD0154')
        self.continuation_bits = stix_packets.get('NIXD0159')
        self.counts = stix_packets.get('NIX00065')

    def to_hdul(self):
        """
        Create a X-ray L0 HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = xray_l0_fits(self.num_structures, self.num_samples)

        # Control
        hdul[-1].data.TC_PACKET_ID_REF = self.tc_packet_id_ref
        hdul[-1].data.TC_PACKET_SEQ_CONTROL = self.tc_packet_seq_control
        hdul[-1].data.REQUEST_ID = self.request_id
        hdul[-1].data.COMPRESSION_SCHEME_COUNT_SKM = self.compression_scheme_counts
        hdul[-1].data.COMPRESSION_SCHEME_TRIGG_SKM = self.compression_scheme_trig
        hdul[-1].data.TIME_STAMP = self.time_stamp
        hdul[-1].data.NUM_STRUCTURES = self.num_structures
        hdul[-1].data.START_TIME = self.start_time
        hdul[-1].data.RCR = self.rcr
        hdul[-1].data.INTEGRATION_DURATION = self.integration_duration
        hdul[-1].data.PIXEL_MASK = self.pixel_mask
        hdul[-1].data.DETECTOR_MASK = self.detector_mask

        for i in range(16):
            hdul[-1].data[f'TRIGGERS_{i}'] = getattr(self, f'triggers_{i}')

        # Data
        hdul[1].data.NUM_SAMPLES = self.num_samples
        hdul[1].data.PIXEL_ID = self.pixel_id
        hdul[1].data.DETECTOR_ID = self.detector_id
        hdul[1].data.CHANNEL = self.channel
        hdul[1].data.CONTINUATION_BITS = self.continuation_bits

        # TODO remove hack for testing
        hdul[1].data.COUNTS = np.pad(np.array(self.counts), (self.num_samples - len(self.counts))//2)

        return hdul


class XrayL1:
    pass


class XrayL2:
    pass


class Spectrogram:
    pass


class Aspect:
    pass
