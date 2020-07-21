"""
STIX science data products
"""
from datetime import timedelta
from itertools import product
from math import modf

import numpy as np

from stix.core.stix_datetime import scet_to_datetime
from stix.fits.io.science import xray_l0_fits, xray_l1l2_fits, aspect, xray_l3_fits, \
    xray_spectrogram
from stix.fits.products.quicklook import get_energies_from_mask


class BaseProduct:
    """
    X-ray Level 0 data
    """
    def __init__(self, packets, eng_packet):

        # Control
        self.tc_packet_id_ref = np.array(packets.get('NIX00001')[0], np.uint16)
        self.tc_packet_seq_control = np.array(packets.get('NIX00002')[0], np.uint16)
        self.request_id = np.array(packets.get('NIX00037')[0], np.uint32)
        self.compression_scheme_counts = np.array((packets['NIXD0007'][0],
                                                   packets['NIXD0008'][0],
                                                   packets['NIXD0009'][0]), np.ubyte)
        self.compression_scheme_trig = np.array((packets['NIXD0010'][0],
                                                 packets['NIXD0011'][0],
                                                 packets['NIXD0012'][0]), np.ubyte)
        self.time_stamp = np.array(packets.get('NIX00402')[0])

        # TODO seems off
        fine, coarse = modf(self.time_stamp)
        self.scet_coarse = np.array(int(coarse), np.uint32).reshape(1,)
        self.scet_fine = np.array(int(fine * 2**16), np.uint16).reshape(1,)

        self.integration_duration = (packets.get('NIX00405', [0])[0] + 1) * 0.1

        self.obs_utc = scet_to_datetime(f'{self.scet_coarse[0]}:{self.scet_fine[0]}')
        self.obs_beg = self.obs_utc
        self.obs_end = self.obs_beg + timedelta(seconds=self.integration_duration)
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        self.structures = np.array(packets.get('NIX00403'), np.uint16)
        self.num_structures = sum(self.structures)


class XrayL0(BaseProduct):
    """
    X-ray Level 0 data
    """
    def __init__(self, packets, eng_packets):

        # Header / Control
        super().__init__(packets, eng_packets)
        self.start_time = (np.array(packets.get('NIX00404'), np.uint16) + 1) * 0.1
        self.rcr = np.array(packets.get('NIX00401')[0], np.ubyte)
        self.integration_duration = (np.array(packets.get('NIX00405')[0], np.uint16) + 1) * 0.1
        pixel_masks = [np.array([bool(int(x)) for x in format(packets.get('NIXD0407')[i], '012b')])
                       for i in range(len(packets.get('NIXD0407')))]
        self.pixel_mask = np.array(pixel_masks)
        detector_masks = [np.array([bool(int(x)) for x in
                                    format(packets.get('NIX00407')[i], '032b')])
                          for i in range(len(packets.get('NIX00407')))]
        self.detector_mask = np.array(detector_masks)
        self.triggers = np.array([packets.get(f'NIX00{i}') for i in range(408, 424)], np.uint32).T

        self.num_detectors = 32
        self.num_energies = 32
        self.num_pixels = 12

        # Data
        self.samples = np.array(packets.get('NIX00406'), np.uint16)
        self.num_samples = sum(self.samples)
        self.pixel_id = np.array(packets.get('NIXD0158'), np.ubyte)
        self.detector_id = np.array(packets.get('NIXD0153'), np.ubyte)
        self.channel = np.array(packets.get('NIXD0154'), np.ubyte)
        self.continuation_bits = packets.get('NIXD0159', np.ubyte)

        # Find contiguous time indices
        unique_times = sorted(set(self.start_time))
        self.num_times = len(unique_times)
        time_indices = [np.argwhere(self.start_time == st) for st in unique_times]

        rt = []
        for tim, num in zip(self.start_time, self.samples):
            rt.extend([tim]*num)

        self.raw_time = np.array(rt, np.uint16)

        # Create time axis time x 32 (one for each detector)
        self.time = np.array([np.repeat(t, 32) for t in unique_times]).flatten()

        # Create full count array 0 are not send down, if cb = 0 so 1 count, for cb 1 just extract
        # and for cb 2 extract and sum
        raw_counts = packets.get('NIX00065')
        counts_1d = []
        raw_count_index = 0
        for cb in self.continuation_bits:
            if cb == 0:
                counts_1d.append(1)
            elif cb == 1:
                cur_count = raw_counts[raw_count_index]
                counts_1d.append(cur_count)
                raw_count_index += cb
            elif cb == 2:
                cur_count = raw_counts[raw_count_index:(raw_count_index + cb)]
                combined_count = int.from_bytes(cur_count[0].to_bytes(2, 'big')
                                       + cur_count[1].to_bytes(1, 'big'), 'big')
                counts_1d.append(combined_count)
                raw_count_index += cb
            else:
                raise ValueError(f'Continuation bits value of {cb} not allowed (0, 1, 2)')
        counts_1d = np.array(counts_1d, np.uint16)
        self.raw_counts = counts_1d

        # Create final count array with 3 dimensions: unique times * 32 det, 32 energies, 12 pixels
        counts = np.zeros((len(unique_times)*self.num_detectors, self.num_energies,
                           self.num_pixels), np.uint16)

        # for i in range(self.num_samples):
        #     tid = np.argwhere(self.raw_counts == unique_times)

        start_index = 0
        for i, time_index in enumerate(time_indices):
            end_index = np.uint32(start_index + np.sum(self.samples[time_index]))

            for did, cid, pid in product(range(self.num_detectors), range(self.num_energies),
                                         range(self.num_pixels)):
                index_1d = ((self.detector_id == did) & (self.channel == cid)
                            & (self.pixel_id == pid))
                cur_count = counts_1d[start_index:end_index][index_1d[start_index:end_index]]
                # If we have a count assign it other wise do nothing as 0
                if cur_count:
                    counts[(i*32)+did, cid, pid] = cur_count[0]

            start_index = end_index

        self.counts = counts

    def to_hdul(self):
        """
        Create a X-ray L0 HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = xray_l0_fits(self.num_structures, self.num_samples, self.num_times,
                            self.num_energies, self.num_pixels)

        # Control
        hdul[-1].data['TC_PACKET_ID_REF'] = self.tc_packet_id_ref
        hdul[-1].data['TC_PACKET_SEQ_CONTROL'] = self.tc_packet_seq_control
        hdul[-1].data['REQUEST_ID'] = self.request_id
        hdul[-1].data['COMPRESSION_SCHEME_COUNT_SKM'] = self.compression_scheme_counts
        hdul[-1].data['COMPRESSION_SCHEME_TRIGG_SKM'] = self.compression_scheme_trig
        hdul[-1].data['TIME_STAMP'] = self.time_stamp
        hdul[-1].data['NUM_STRUCTURES'] = self.num_structures
        hdul[-1].data['RCR'] = self.rcr
        hdul[-1].data['INTEGRATION_DURATION'] = self.integration_duration
        hdul[-1].data['PIXEL_MASK'] = self.pixel_mask
        hdul[-1].data['DETECTOR_MASK'] = self.detector_mask
        hdul[-1].data['NUM_SAMPLES'] = self.num_samples
        hdul[-1].data['TRIGGERS'] = self.triggers

        # Raw Data
        hdul[1].data['RAW_TIME'] = self.raw_time
        hdul[1].data['PIXEL_ID'] = self.pixel_id
        hdul[1].data['DETECTOR_ID'] = self.detector_id
        hdul[1].data['CHANNEL'] = self.channel
        hdul[1].data['CONTINUATION_BITS'] = self.continuation_bits
        hdul[1].data['RAW_COUNTS'] = self.raw_counts

        # Reshaped data
        hdul[2].data['TIME'] = self.time
        hdul[2].data['COUNTS'] = self.counts

        e_low, e_high = get_energies_from_mask()
        hdul[-2].data['E_MIN'] = e_low
        hdul[-2].data['E_MAX'] = e_high
        hdul[-2].data['CHANNEL'] = list(range(len(e_low)))

        return hdul


class XrayL1(BaseProduct):
    """
    X-ray Compression Level 1/2 data
    """
    def __init__(self, packets, eng_packets):
        # Control
        super().__init__(packets, eng_packets)

        self.delta_time = (np.array(packets['NIX00441'], np.uint16) + 1) * 0.1
        self.unique_times = np.unique(self.delta_time)

        self.rcr = np.array(packets['NIX00401'], np.ubyte)
        self.num_pixel_sets = np.array(packets['NIX00442'], np.ubyte)
        pixel_masks = [np.array([bool(int(x)) for x in format(packets.get('NIXD0407')[i], '012b')])
                       for i in range(len(packets.get('NIXD0407')))]
        self.pixel_masks = np.array(pixel_masks).reshape(self.num_structures,
                                                         self.num_pixel_sets[0], 12)
        detector_masks = [np.array([bool(int(x)) for x in
                                    format(packets.get('NIX00407')[i], '032b')])
                          for i in range(len(packets.get('NIX00407')))]
        self.detector_masks = detector_masks
        self.duration = (np.array(packets['NIX00405'], np.uint16) + 1) * 0.1
        self.triggers = np.array([eng_packets.get(f'NIX00{i}') for i in range(242, 258)],
                                 np.ubyte).T
        self.num_energy_groups = np.array(packets['NIX00258'], np.ubyte)
        self.total_energy_groups = np.sum(self.num_energy_groups).astype(np.uint32)

        self.e_low = np.array(packets['NIXD0016'], np.ubyte)
        self.e_high = np.array(packets['NIXD0017'], np.ubyte)
        self.num_energies = np.unique(self.e_low).size

        self.num_data_elements = packets['NIX00259']
        self.num_detectors = np.sum(detector_masks[0])

        time = np.array([], np.uint32)
        for dt in self.unique_times:
            nt = self.num_detectors
            time = np.append(time, np.repeat(dt, nt))

        self.time = time

        # time x energy x detector x pixel
        counts = np.array(
            eng_packets['NIX00260'], np.uint16).reshape(self.unique_times.size, self.num_energies,
                                                        self.num_detectors, self.num_pixel_sets[0])

        # To match l0 data should be (time x detector) x energy x pixel
        self.num_recs = self.unique_times.size * self.num_detectors
        counts = counts.transpose((0, 2, 1, 3))
        counts = counts.reshape(self.num_recs, self.num_energies, self.num_pixel_sets[0])

        self.counts = counts

    def to_hdul(self):
        """
        Create a Xray-L1/2 HDUL.


        Returns
        -------
        `astropy.io.fits.HUDList`
            The Xray-L1/L2 HDUL
        """
        hdul = xray_l1l2_fits(self.num_structures, self.num_detectors, self.num_energies,
                              self.num_pixel_sets[0], self.num_recs)

        # Control
        hdul[-1].data['TC_PACKET_ID_REF'] = self.tc_packet_id_ref
        hdul[-1].data['TC_PACKET_SEQ_CONTROL'] = self.tc_packet_seq_control
        hdul[-1].data['REQUEST_ID'] = self.request_id
        hdul[-1].data['COMPRESSION_SCHEME_COUNT_SKM'] = self.compression_scheme_counts
        hdul[-1].data['COMPRESSION_SCHEME_TRIGG_SKM'] = self.compression_scheme_trig
        hdul[-1].data['TIME_STAMP'] = self.time_stamp
        hdul[-1].data['NUM_STRUCTURES'] = self.num_structures
        hdul[-1].data['DELTA_TIME'] = self.delta_time
        hdul[-1].data['DURATION'] = self.duration
        hdul[-1].data['RCR'] = self.rcr
        hdul[-1].data['NUM_PIXEL_SET'] = self.num_pixel_sets
        hdul[-1].data['PIXEL_MASKS'] = self.pixel_masks
        hdul[-1].data['DETECTOR_MASKS'] = self.detector_masks
        hdul[-1].data['TRIGGERS'] = np.array(self.triggers)
        hdul[-1].data['NUM_ENERGY_GROUPS'] = self.num_energy_groups

        # Data
        hdul[1].data['TIME'] = self.time
        # hdul[1].data['E_LOW'] = self.e_low
        # hdul[1].data['E_HIGH'] = self.e_high
        # hdul[1].data['NUM_DATA_ELEMENTS'] = self.num_data_elements
        hdul[1].data['COUNTS'] = self.counts

        e_low, e_high = get_energies_from_mask()
        hdul[-2].data['E_MIN'] = e_low
        hdul[-2].data['E_MAX'] = e_high
        hdul[-2].data['CHANNEL'] = list(range(len(e_low)))

        return hdul


class XrayL2(XrayL1):
    """
    X-ray Compression Level 2 data
    """
    pass


class XrayL3(BaseProduct):
    """
    X-ray Compression Level 3 data (visibilities)
    """
    def __init__(self, packets, eng_packets):
        # Control
        super().__init__(packets, eng_packets)

        self.delta_time = np.array(packets['NIX00441'])

        time = np.array([])
        for dt in set(self.delta_time):
            i, = np.where(self.delta_time == dt)
            nt = sum(np.array(packets['NIX00258'])[i])
            time = np.append(time, np.repeat(dt, nt))
        self.time = time

        self.rcr = packets['NIX00401']
        self.pixel_mask1 = [int(x) for x in format(packets['NIXD0407'][0], '012b')]
        self.pixel_mask2 = [int(x) for x in format(packets['NIXD0444'][0], '012b')]
        self.pixel_mask3 = [int(x) for x in format(packets['NIXD0445'][0], '012b')]
        self.pixel_mask4 = [int(x) for x in format(packets['NIXD0446'][0], '012b')]
        self.pixel_mask5 = [int(x) for x in format(packets['NIXD0447'][0], '012b')]
        self.detector_masks = [int(i) for i in format(packets['NIX00407'][0], 'b')]
        self.duration = (packets['NIX00405'][0]) * 0.1
        self.triggers = np.array([packets[f'NIX00{i}'] for i in range(242, 258)]).T
        self.num_energy_groups = sum(packets['NIX00258'])

        # Data
        self.e_low = packets['NIXD0016']
        self.e_high = packets['NIXD0017']
        self.flux = packets['NIX00261']
        self.num_detectors = packets['NIX00262'][0]
        self.detector_id = np.array(packets['NIX00100']).reshape(self.num_energy_groups,
                                                                 self.num_detectors)
        self.visibility = (np.array(packets['NIX00263'])
                           + np.array(packets['NIX00264']) * 1j).reshape(self.num_energy_groups,
                                                                         self.num_detectors)

    def to_hdul(self):
        """
        Create a Xray-L3 HDUL.

        Returns
        -------
        `astropy.io.fits.HUDList`
            The Xray-L3 HDUL
        """
        hdul = xray_l3_fits(self.num_structures, self.num_energy_groups, self.num_detectors)

        # Control
        hdul[-1].data['TC_PACKET_ID_REF'] = self.tc_packet_id_ref
        hdul[-1].data['TC_PACKET_SEQ_CONTROL'] = self.tc_packet_seq_control
        hdul[-1].data['REQUEST_ID'] = self.request_id
        hdul[-1].data['COMPRESSION_SCHEME_COUNT_SKM'] = self.compression_scheme_counts
        hdul[-1].data['COMPRESSION_SCHEME_TRIGG_SKM'] = self.compression_scheme_trig
        hdul[-1].data['TIME_STAMP'] = self.time_stamp
        hdul[-1].data['NUM_STRUCTURES'] = self.num_structures
        hdul[-1].data['DELTA_TIME'] = self.delta_time
        hdul[-1].data['RCR'] = self.rcr
        hdul[-1].data['INTEGRATION_DURATION'] = self.integration_duration
        hdul[-1].data['PIXEL_MASK1'] = self.pixel_mask1
        hdul[-1].data['PIXEL_MASK2'] = self.pixel_mask2
        hdul[-1].data['PIXEL_MASK3'] = self.pixel_mask3
        hdul[-1].data['PIXEL_MASK4'] = self.pixel_mask4
        hdul[-1].data['PIXEL_MASK5'] = self.pixel_mask5
        hdul[-1].data['DETECTOR_MASKS'] = self.detector_masks
        hdul[-1].data['TRIGGERS'] = self.triggers
        hdul[-1].data['NUM_ENERGY_GROUPS'] = self.num_energy_groups

        # Data
        hdul[1].data['TIME'] = self.time
        hdul[1].data['E_LOW'] = self.e_low
        hdul[1].data['E_HIGH'] = self.e_high
        hdul[1].data['FLUX'] = self.flux
        hdul[1].data['DETECTOR_ID'] = self.detector_id
        hdul[1].data['VISIBILITY'] = self.visibility

        return hdul


class Spectrogram(BaseProduct):
    """
    Spectrogram data
    """
    def __init__(self, packets, eng_packets):
        # Control
        super().__init__(packets, eng_packets)

        self.pixel_mask = [int(x) for x in format(packets['NIXD0407'][0], '012b')]
        self.detector_mask = [int(x) for x in format(packets['NIX00407'][0], '032b')]
        self.rcr = packets['NIX00401'][0]
        self.e_min = packets['NIXD0442'][0]
        self.e_max = packets['NIXD0443'][0]
        self.energy_unit = packets['NIXD0019'][0] + 1
        self.num_times = np.sum(packets['NIX00089'])

        # Data
        self.delta_time = (np.array(packets['NIX00441'], np.uint16) + 1) * 0.1

        self.obs_end = self.obs_beg + timedelta(seconds=self.delta_time.max())
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        self.combined_triggers = eng_packets['NIX00267']
        self.num_energies = packets['NIX00270']
        self.counts = np.array(eng_packets['NIX00268']).reshape(self.num_times,
                                                                self.num_energies[0])
        self.closing_time_offset = (np.array(packets['NIX00269'][0], np.uint16) + 1) * 0.1

    def to_hdul(self):
        """
        Create a Spectrogram HDUL.

        Returns
        -------
        `astropy.io.fits.HUDList`
            The Xray-L3 HDUL
        """

        # Control
        hdul = xray_spectrogram(self.num_structures, self.num_times, self.num_energies[0])
        hdul[-1].data['TC_PACKET_ID_REF'] = self.tc_packet_id_ref
        hdul[-1].data['TC_PACKET_SEQ_CONTROL'] = self.tc_packet_seq_control
        hdul[-1].data['REQUEST_ID'] = self.request_id
        hdul[-1].data['COMPRESSION_SCHEME_COUNT_SKM'] = self.compression_scheme_counts
        hdul[-1].data['COMPRESSION_SCHEME_TRIGG_SKM'] = self.compression_scheme_trig
        hdul[-1].data['TIME_STAMP'] = self.time_stamp
        hdul[-1].data['NUM_STRUCTURES'] = self.num_structures

        hdul[-1].data['PIXEL_MASK'] = self.pixel_mask
        hdul[-1].data['DETECTOR_MASK'] = self.detector_mask
        hdul[-1].data['RCR'] = self.rcr
        hdul[-1].data['E_MIN'] = self.e_min
        hdul[-1].data['E_MAX'] = self.e_max
        hdul[-1].data['E_BIN_WIDTH'] = self.energy_unit

        hdul[1].data['DELTA_TIME'] = self.delta_time
        hdul[1].data['COMBINED_TRIGGERS'] = self.combined_triggers
        hdul[1].data['COUNTS'] = self.counts
        hdul[1].data['CLOSE_TIME_OFFSET'] = self.closing_time_offset

        e_low, e_high = get_energies_from_mask()
        index = list(range(self.e_min, self.e_max+1, self.energy_unit))
        hdul[-2].data['E_MIN'] = np.asarray(e_low)[index]
        hdul[-2].data['E_MAX'] = np.asarray(e_high)[index]
        hdul[-2].data['CHANNEL'] = index

        return hdul


class Aspect:
    """
    Aspect
    """
    def __init__(self, packets, eng_packets):
        # Header
        self.scet_coarse = packets['NIX00445']
        self.scet_fine = packets['NIX00446']
        self.obs_utc = scet_to_datetime(f'{self.scet_coarse[0]}:{self.scet_fine[0]}')
        self.obs_beg = self.obs_utc
        self.obs_end = scet_to_datetime(f'{self.scet_coarse[-1]}:{self.scet_fine[-1]}')
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        self.summing_value = packets['NIX00088'][0]
        self.averaging_value = packets['NIX00490'][0]
        self.delta_time = (self.summing_value * self.averaging_value / 1000.0)
        self.samples = packets['NIX00089']
        self.num_samples = sum(packets['NIX00089'])

        times = [scet_to_datetime(f"{packets['NIX00445'][i]}:{packets['NIX00446'][i]}") for i in
                 range(len(self.scet_coarse))]
        base_times = np.array(times) - times[0]
        time = np.array([])
        for bt, sample in zip(base_times, self.samples):
            cur_time = bt.total_seconds() + np.arange(sample) * self.delta_time
            time = np.concatenate((time, cur_time))

        # Data
        self.time = time
        self.cha_diode0 = packets['NIX00090']
        self.cha_diode1 = packets['NIX00091']
        self.chb_diode0 = packets['NIX00092']
        self.chb_diode1 = packets['NIX00093']

    def to_hdul(self):
        """
        Create a Aspect HDUL.

        Returns
        -------
        `astropy.io.fits.HUDList`
            Aspect HDUL
        """
        hdul = aspect(self.num_samples)

        # Control
        hdul[-1].data['SUMMING_VALUE'] = self.summing_value
        hdul[-1].data['NUM_SAMPLES'] = self.num_samples

        # Data
        hdul[1].data['TIME'] = self.time
        hdul[1].data['CHA_DIODE0'] = self.cha_diode0
        hdul[1].data['CHA_DIODE1'] = self.cha_diode1
        hdul[1].data['CHB_DIODE0'] = self.chb_diode0
        hdul[1].data['CHB_DIODE1'] = self.chb_diode1

        return hdul
