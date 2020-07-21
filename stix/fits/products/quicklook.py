"""
High level STIX data products created from single stand alone packets or a sequence of packects.
"""
from datetime import timedelta
from itertools import chain

import astropy.units as u
import numpy as np
from astropy.time import Time

from stix.core.stix_datetime import scet_to_datetime
from stix.fits.io.quicklook import light_curve_fits, flare_flag_location_fits, \
    background_fits, spectra_fits, variance_fits, \
    calibration_spectra_fits, tm_management_and_flare_list_fits
from stix.utils.logger import get_logger

logger = get_logger(__name__)

__all__ = ['LightCurve', 'Background', 'Spectra', 'Variance', 'CalibrationSpectra',
           'FlareFlagAndLocation', 'TMManagementAndFlareList', 'get_energies_from_mask']

ENERGY_CHANNELS = {
    0: {'channel_edge': 0, 'energy_edge': 0, 'e_lower': 0.0, 'e_upper': 4.0, 'bin_width': 4.0,
        'dE_E': 2.000, 'ql_channel': None},
    1: {'channel_edge': 1, 'energy_edge': 4, 'e_lower': 4.0, 'e_upper': 5.0, 'bin_width': 1.0,
        'dE_E': 0.222, 'ql_channel': 0},
    2: {'channel_edge': 2, 'energy_edge': 5, 'e_lower': 5.0, 'e_upper': 6.0, 'bin_width': 1.0,
        'dE_E': 0.182, 'ql_channel': 0},
    3: {'channel_edge': 3, 'energy_edge': 6, 'e_lower': 6.0, 'e_upper': 7.0, 'bin_width': 1.0,
        'dE_E': 0.154, 'ql_channel': 0},
    4: {'channel_edge': 4, 'energy_edge': 7, 'e_lower': 7.0, 'e_upper': 8.0, 'bin_width': 1.0,
        'dE_E': 0.133, 'ql_channel': 0},
    5: {'channel_edge': 5, 'energy_edge': 8, 'e_lower': 8.0, 'e_upper': 9.0, 'bin_width': 1.0,
        'dE_E': 0.118, 'ql_channel': 0},
    6: {'channel_edge': 6, 'energy_edge': 9, 'e_lower': 9.0, 'e_upper': 10.0, 'bin_width': 1.0,
        'dE_E': 0.105, 'ql_channel': 0},
    7: {'channel_edge': 7, 'energy_edge': 10, 'e_lower': 10.0, 'e_upper': 11.0, 'bin_width': 1.0,
        'dE_E': 0.095, 'ql_channel': 1},
    8: {'channel_edge': 8, 'energy_edge': 11, 'e_lower': 11.0, 'e_upper': 12.0, 'bin_width': 1.0,
        'dE_E': 0.087, 'ql_channel': 1},
    9: {'channel_edge': 9, 'energy_edge': 12, 'e_lower': 12.0, 'e_upper': 13.0, 'bin_width': 1.0,
        'dE_E': 0.080, 'ql_channel': 1},
    10: {'channel_edge': 10, 'energy_edge': 13, 'e_lower': 13.0, 'e_upper': 14.0, 'bin_width': 1.0,
         'dE_E': 0.074, 'ql_channel': 1},
    11: {'channel_edge': 11, 'energy_edge': 14, 'e_lower': 14.0, 'e_upper': 15.0, 'bin_width': 1.0,
         'dE_E': 0.069, 'ql_channel': 1},
    12: {'channel_edge': 12, 'energy_edge': 15, 'e_lower': 15.0, 'e_upper': 16.0, 'bin_width': 1.0,
         'dE_E': 0.065, 'ql_channel': 2},
    13: {'channel_edge': 13, 'energy_edge': 16, 'e_lower': 16.0, 'e_upper': 17.0, 'bin_width': 1.0,
         'dE_E': 0.061, 'ql_channel': 2},
    14: {'channel_edge': 14, 'energy_edge': 18, 'e_lower': 18.0, 'e_upper': 20.0, 'bin_width': 2.0,
         'dE_E': 0.105, 'ql_channel': 2},
    15: {'channel_edge': 15, 'energy_edge': 20, 'e_lower': 20.0, 'e_upper': 22.0, 'bin_width': 2.0,
         'dE_E': 0.095, 'ql_channel': 2},
    16: {'channel_edge': 16, 'energy_edge': 22, 'e_lower': 22.0, 'e_upper': 25.0, 'bin_width': 3.0,
         'dE_E': 0.128, 'ql_channel': 2},
    17: {'channel_edge': 17, 'energy_edge': 25, 'e_lower': 25.0, 'e_upper': 28.0, 'bin_width': 3.0,
         'dE_E': 0.113, 'ql_channel': 3},
    18: {'channel_edge': 18, 'energy_edge': 28, 'e_lower': 28.0, 'e_upper': 32.0, 'bin_width': 4.0,
         'dE_E': 0.133, 'ql_channel': 3},
    19: {'channel_edge': 19, 'energy_edge': 32, 'e_lower': 32.0, 'e_upper': 36.0, 'bin_width': 4.0,
         'dE_E': 0.118, 'ql_channel': 3},
    20: {'channel_edge': 20, 'energy_edge': 36, 'e_lower': 36.0, 'e_upper': 40.0, 'bin_width': 4.0,
         'dE_E': 0.105, 'ql_channel': 3},
    21: {'channel_edge': 21, 'energy_edge': 40, 'e_lower': 40.0, 'e_upper': 45.0, 'bin_width': 5.0,
         'dE_E': 0.118, 'ql_channel': 3},
    22: {'channel_edge': 22, 'energy_edge': 45, 'e_lower': 45.0, 'e_upper': 50.0, 'bin_width': 5.0,
         'dE_E': 0.105, 'ql_channel': 3},
    23: {'channel_edge': 23, 'energy_edge': 50, 'e_lower': 50.0, 'e_upper': 56.0, 'bin_width': 6.0,
         'dE_E': 0.113, 'ql_channel': 4},
    24: {'channel_edge': 24, 'energy_edge': 56, 'e_lower': 56.0, 'e_upper': 63.0, 'bin_width': 7.0,
         'dE_E': 0.118, 'ql_channel': 4},
    25: {'channel_edge': 25, 'energy_edge': 63, 'e_lower': 63.0, 'e_upper': 70.0, 'bin_width': 7.0,
         'dE_E': 0.105, 'ql_channel': 4},
    26: {'channel_edge': 26, 'energy_edge': 70, 'e_lower': 70.0, 'e_upper': 76.0, 'bin_width': 6.0,
         'dE_E': 0.082, 'ql_channel': 4},
    27: {'channel_edge': 27, 'energy_edge': 76, 'e_lower': 76.0, 'e_upper': 84.0, 'bin_width': 8.0,
         'dE_E': 0.100, 'ql_channel': 4},
    28: {'channel_edge': 28, 'energy_edge': 84, 'e_lower': 84.0, 'e_upper': 100.0,
         'bin_width': 16.0, 'dE_El': 0.174, 'ql_channel': 4},
    29: {'channel_edge': 29, 'energy_edge': 100, 'e_lower': 100.0, 'e_upper': 120.0,
         'bin_width': 20.0, 'dE_El': 0.182, 'ql_channel': 4},
    30: {'channel_edge': 30, 'energy_edge': 120, 'e_lower': 120.0, 'e_upper': 150.0,
         'bin_width': 30.0, 'dE_El': 0.222, 'ql_channel': 4},
    31: {'channel_edge': 31, 'energy_edge': 150, 'e_lower': 150.0, 'e_upper': np.inf,
         'bin_width': np.inf, 'dE_E': np.inf, 'ql_channel': None}
}


class BaseProduct:
    """
    Basic STIX data product.
    """
    def __init__(self, packets):
        # Header
        self.energy_bin_mask = None
        self.samples = None
        self.scet_coarse = np.array(packets['NIX00445'], np.uint32)
        self.scet_fine = np.array(packets.get('NIX00446', [0]), np.uint32)
        self.obs_utc = scet_to_datetime(f'{self.scet_coarse[0]}:{self.scet_fine[0]}')
        self.obs_beg = self.obs_utc
        # time are recored in 0.1 seconds and indexed from 0 -> 0.1 s, 1->0.2s etc
        integration_times = (np.array(packets.get('NIX00405', [0]), np.uint16) + 1) * 0.1
        if not np.all(integration_times == integration_times[0]):
            logger.warning(f'Integration time changed in packet sequence')
        self.integration_time = integration_times[0]

    def _get_energy_channels(self, hdul):
        e_low, e_high = get_energies_from_mask(self.energy_bin_mask)
        hdul[-2].data['E_MIN'] = e_low
        hdul[-2].data['E_MAX'] = e_high
        hdul[-2].data['CHANNEL'] = list(range(len(e_low)))

    def _get_time(self, spectra=False):
        # Replicate packet time for each sample
        base_times = Time(list(chain(
            *[[scet_to_datetime(f'{self.scet_coarse[i]}:{self.scet_fine[i]}')] * n for i, n in
              enumerate(self.samples)])))
        # For each sample generate sample number and multiply by duration and apply unit
        delta_times = np.array(list(chain(
            *[list(range(sample)) for sample in self.samples]))) * self.integration_time << u.s
        # Add the delta time to base times and convert to relative from start time
        times = base_times + delta_times
        times -= times[0]
        return times.to('s').value

    @staticmethod
    def _get_compression_scheme(packets, nix1, nix2, nix3):
        comp_counts = np.array((packets[nix1], packets[nix2],
                                packets[nix3]), np.ubyte).T
        if not np.all(comp_counts == comp_counts[0, :]):
            logger.warning(f'Compression scheme changed in packet sequence')
        return comp_counts[0]

    @staticmethod
    def _get_energy_bins(packets, nixlower, nixuppper):
        energy_bin_mask = np.array(packets[nixlower], np.uint32)
        energy_bin_mask_uppper = np.array(packets[nixuppper], np.bool8)
        if not np.all((energy_bin_mask == energy_bin_mask[0]) &
                      (energy_bin_mask_uppper == energy_bin_mask_uppper[0])):
            logger.warning(f'Pixel mask changed in packet sequence')

        full_energy_mask = format(energy_bin_mask_uppper[0], 'b') + \
            format(energy_bin_mask[0], 'b').zfill(32)
        full_energy_mask = np.array([np.array(d).astype(np.bool8) for d in
                                     full_energy_mask][::-1])  # reverse ind
        return full_energy_mask

    @staticmethod
    def _get_detector_mask(packets):
        detector_masks = np.array([
            [bool(int(x)) for x in format(packets.get('NIX00407')[i], '032b')][::-1]  # reverse ind
            for i in range(len(packets.get('NIX00407')))], bool)

        if not np.all(detector_masks == detector_masks[0, :]):
            logger.warning(f'Detector mask changed in packet sequence')
        return detector_masks[0]

    @staticmethod
    def _get_pixel_mask(packets):
        pixel_masks = np.array([
            [bool(int(x)) for x in format(packets.get('NIXD0407')[i], '012b')][::-1]  # reverse ind
            for i in range(len(packets.get('NIXD0407')))], bool)

        if not np.all(pixel_masks == pixel_masks[0, :]):
            logger.warning(f'Pixel mask changed in packet sequence')
        return pixel_masks[0]

    @staticmethod
    def _get_num_energies(packets):
        """

        Parameters
        ----------
        packets

        Returns
        -------

        """
        if len(set(packets['NIX00270'])) != 1:
            logger.warning(f'Numer of energies changed in packet sequence')
        return packets['NIX00270'][0]

    @staticmethod
    def _get_unique(packets, param_name, dtype):
        """
        Get a unique parameter raise warning if not unique

        Parameters
        ----------
        param_name : str
            STIX parameter name eg NIX00001
        dtype : np.dtype
            Dtype to case to eg. np.uint16/np.uint32

        Returns
        -------
        np.array
            First value even if not unique
        """
        param = np.array(packets[param_name], dtype)
        if not np.all(param == param[0]):
            logger.warning('%s has changed in complete packet sequence', param_name)
        return param[0]


class LightCurve(BaseProduct):
    """
    Quick Look Light Curve data product.
    """
    def __init__(self, packets, eng_packets):
        # Header
        super().__init__(packets)

        # CONTROL
        self.detector_mask = self._get_detector_mask(packets)
        self.pixel_mask = self._get_pixel_mask(packets)
        self.energy_bin_mask = self._get_energy_bins(packets, 'NIX00266', 'NIXD0107')
        self.compression_scheme_counts = self._get_compression_scheme(packets, 'NIXD0101',
                                                                      'NIXD0102', 'NIXD0103')
        self.compression_scheme_triggers = self._get_compression_scheme(packets, 'NIXD0104',
                                                                        'NIXD0105', 'NIXD0106')
        self.num_energies = self._get_num_energies(packets)
        # Repeated for each energy so only use every nth sample
        self.samples = packets['NIX00271'][::self.num_energies]
        self.num_samples = sum(self.samples)

        self.obs_end = scet_to_datetime(f'{self.scet_coarse[-1]}:{self.scet_fine[-1]}') + \
            timedelta(seconds=self.samples[-1]*self.integration_time)
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        self.time = self._get_time()
        # self.timedel = (times[1:]-times[:-1]).to('s').value

        counts = eng_packets['NIX00272']
        flat_indices = np.cumsum([0, *self.samples])*self.num_energies
        arrays = [
            np.array(counts[flat_indices[i]:flat_indices[i + 1]]).reshape(self.num_energies, sample)
            for i, sample in enumerate(self.samples)]

        self.light_curves = np.concatenate(arrays, axis=1).T
        self.triggers = eng_packets['NIX00274']
        self.rcr = packets['NIX00276']

    def to_hdul(self):
        """
        Create a LightCurve HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = light_curve_fits(self.num_samples, self.num_energies)

        # Control
        hdul[-1].data['INTEGRATION_TIME'] = self.integration_time
        hdul[-1].data['DETECTOR_MASK'] = self.detector_mask
        hdul[-1].data['PIXEL_MASK'] = self.pixel_mask
        hdul[-1].data['ENERGY_BIN_MASK'] = self.energy_bin_mask
        hdul[-1].data['COMPRESSION_SCHEME_COUNTS_SKM'] = self.compression_scheme_counts
        hdul[-1].data['COMPRESSION_SCHEME_TRIGGERS_SKM'] = self.compression_scheme_counts

        # Data
        hdul[1].data['TIME'] = self.time
        # hdul[1].data['TIMEDEL'] = self.timedel
        hdul[1].data['COUNTS'] = self.light_curves
        hdul[1].data['TRIGGERS'] = self.triggers
        hdul[1].data['RATE_CONTROL_REGIME'] = self.rcr

        hdul[1].header.update({'DATA_MAX': np.max(self.light_curves),
                               'DATA_MIN': np.min(self.light_curves),
                               'BUNIT': 'W m-2'})

        # Energy
        self._get_energy_channels(hdul)

        return hdul


class Background(BaseProduct):
    """
    Background product.
    """
    def __init__(self, packets, eng_packets):
        # Header
        super().__init__(packets)

        # Control
        self.energy_bin_mask = self._get_energy_bins(packets, 'NIX00266', 'NIXD0111')
        self.compression_scheme_background = self._get_compression_scheme(packets, 'NIXD0108',
                                                                          'NIXD0109', 'NIXD0109')
        self.compression_scheme_triggers = self._get_compression_scheme(packets, 'NIXD0112',
                                                                        'NIXD0113', 'NIXD0114')
        # Data
        self.num_energies = self._get_num_energies(packets)
        self.samples = packets['NIX00277'][::self.num_energies]
        self.num_samples = sum(self.samples)

        self.obs_end = scet_to_datetime(f'{self.scet_coarse[-1]}:{self.scet_fine[-1]}') + \
            timedelta(seconds=self.samples[-1]*self.integration_time)
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        self.time = self._get_time()

        counts = eng_packets['NIX00278']
        flat_indices = np.cumsum([0, *self.samples]) * self.num_energies
        arrays = [
            np.array(counts[flat_indices[i]:flat_indices[i + 1]]).reshape(self.num_energies, sample)
            for i, sample in enumerate(self.samples)]

        self.background = np.concatenate(arrays, axis=1).T
        self.triggers = eng_packets.get('NIX00274')

    def to_hdul(self):
        """
        Create a Background HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = background_fits(self.num_samples, self.num_energies)

        # Control
        hdul[-1].data['INTEGRATION_TIME'] = self.integration_time
        hdul[-1].data['ENERGY_BIN_MASK'] = self.energy_bin_mask
        hdul[-1].data['COMPRESSION_SCHEME_BACKGROUND_SKM'] = self.compression_scheme_background
        hdul[-1].data['COMPRESSION_SCHEME_TRIGGERS_SKM'] = self.compression_scheme_triggers

        # data
        hdul[1].data['TIME'] = self.time
        # hdul[1].data['TIMEDEL'] = np.full(self.num_samples, self.integration_time)
        hdul[1].data['COUNTS'] = self.background
        hdul[1].data['TRIGGERS'] = self.triggers

        # Energy
        self._get_energy_channels(hdul)

        return hdul


class Spectra(BaseProduct):
    """
    Background product.
    """
    def __init__(self, packets, eng_packets):
        # Header
        super().__init__(packets)

        # Control
        self.pixel_mask = self._get_pixel_mask(packets)
        self.compression_scheme_spectrum = self._get_compression_scheme(packets, 'NIXD0115',
                                                                        'NIXD0116', 'NIXD0117')
        self.compression_scheme_triggers = self._get_compression_scheme(packets, 'NIXD0112',
                                                                        'NIXD0113', 'NIXD0114')
        # Data
        self.samples = packets.get('NIX00089')
        self.num_samples = sum(packets.get('NIX00089'))
        self.num_energies = 32

        self.obs_end = scet_to_datetime(f'{self.scet_coarse[-1]}:{self.scet_fine[-1]}') + \
            timedelta(seconds=self.samples[-1]*self.integration_time)
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        start_time = Time(self.obs_beg)
        start = 0
        times = []
        for i, samples in enumerate(self.samples):
            dt = np.array(packets.get('NIX00485')[start:start + samples]) * self.integration_time
            base_time = Time(scet_to_datetime(f'{self.scet_coarse[i]}:{self.scet_fine[i]}'))
            time = (base_time + (dt << u.s)) - start_time
            times.extend(time.to_value('s'))
            start += samples

        self.time = times

        self.detector_index = np.array(packets.get('NIX00100'), np.ubyte)
        self.spectra = np.array([eng_packets.get('NIX00{}'.format(i)) for i in range(452, 484)],
                                np.uint32).T  # sample x energy
        self.triggers = np.array(eng_packets.get('NIX00484'), np.uint32)
        self.num_integrations = np.array(packets.get('NIX00485'), np.uint16)

    def to_hdul(self):
        """
        Create a Spectra HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = spectra_fits(self.num_samples, self.num_energies)

        # Control
        hdul[-1].data['INTEGRATION_TIME'] = self.integration_time
        hdul[-1].data['PIXEL_MASK'] = self.pixel_mask
        hdul[-1].data['COMPRESSION_SCHEME_COUNTS_SKM'] = self.compression_scheme_spectrum
        hdul[-1].data['COMPRESSION_SCHEME_TRIGGERS_SKM'] = self.compression_scheme_triggers

        # Data
        hdul[1].data['DETECTOR_ID'] = self.detector_index
        hdul[1].data['COUNTS'] = self.spectra
        hdul[1].data['CHANNEL'] = np.array(range(32)).reshape(32, 1).repeat(self.num_samples,
                                                                            axis=1).T
        hdul[1].data['TRIGGERS'] = self.triggers
        hdul[1].data['NUM_INTEGRATIONS'] = self.num_integrations
        hdul[1].data['TIME'] = self.time

        # Energy
        e_low, e_high = get_energies_from_mask()
        hdul[-2].data['E_MIN'] = e_low
        hdul[-2].data['E_MAX'] = e_high
        hdul[-2].data['CHANNEL'] = list(range(len(e_low)))

        return hdul


class Variance(BaseProduct):
    """
    Variance product.
    """
    def __init__(self, packets, eng_packets):
        # Header
        super().__init__(packets)

        # Control
        self.sample_per_variance = np.array(packets.get('NIX00279'), np.ubyte)

        self.detector_mask = self._get_detector_mask(packets)
        self.pixel_mask = self._get_pixel_mask(packets)

        energy_masks = np.array([
            [bool(int(x)) for x in format(packets.get('NIX00282')[i], '032b')]
            for i in range(len(packets.get('NIX00282')))])
        if not np.all(energy_masks == energy_masks[0, :]):
            logger.warning('Energy mask changed in packet sequence')
        self.energy_mask = energy_masks[0]

        self.compression_scheme_variance = self._get_compression_scheme(packets, 'NIXD0118',
                                                                        'NIXD0119', 'NIXD0120')

        # Data
        self.num_energies = 1
        self.samples = packets.get('NIX00280')
        self.num_samples = sum(self.samples)

        self.obs_end = scet_to_datetime(f'{self.scet_coarse[-1]}:{self.scet_fine[-1]}') + \
            timedelta(seconds=self.samples[-1]*self.integration_time)
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2
        self.time = self._get_time()
        self.variance = np.array(eng_packets.get('NIX00281'))

    def to_hdul(self):
        """
        Create a Variance HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = variance_fits(self.num_samples, self.num_energies)

        # Control
        hdul[-1].data['INTEGRATION_TIME'] = self.integration_time
        hdul[-1].data['SAMPLES'] = self.num_samples
        hdul[-1].data['PIXEL_MASK'] = self.pixel_mask
        hdul[-1].data['DETECTOR_MASK'] = self.detector_mask
        hdul[-1].data['ENERGY_MASK'] = self.energy_mask
        hdul[-1].data['COMPRESSION_SCHEME_VARIANCE_SKM'] = self.compression_scheme_variance

        # Data
        hdul[1].data['TIME'] = self.time
        # hdul[1].data['TIMEDEL'] = np.full(self.num_samples, self.integration_time)
        hdul[1].data['VARIANCE'] = self.variance

        # Energy
        e_low, e_high = get_energies_from_mask(self.energy_mask)
        hdul[-2].data['E_MIN'] = e_low
        hdul[-2].data['E_MAX'] = e_high
        hdul[-2].data['CHANNEL'] = 0

        return hdul


class CalibrationSpectra(BaseProduct):
    """
    Calibration Spectra data product.
    """
    def __init__(self, packets, eng_packets):
        # Header
        super().__init__(packets)

        self.scet_coarse = np.array(packets['NIX00445'], np.uint32)
        if not np.all(self.scet_coarse == self.scet_coarse[0]):
            logger.warning('SCET coarse time changed in complete calibration packet sequence')
        self.scet_fine = [0]  # to make compatible with others
        self.obs_utc = scet_to_datetime(f'{self.scet_coarse[0]}:{self.scet_fine[0]}')

        self.duration = self._get_unique(packets, 'NIX00122', np.uint32)

        self.obs_beg = self.obs_utc
        self.obs_end = self.obs_beg + timedelta(seconds=self.duration.astype('float'))
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        # Control
        self.quiet_time = self._get_unique(packets, 'NIX00123', np.uint16)
        self.live_time = self._get_unique(packets, 'NIX00124', np.uint32)
        self.average_temperature = self._get_unique(packets, 'NIX00125', np.uint16)
        self.detector_mask = self._get_detector_mask(packets)
        self.pixel_mask = self._get_pixel_mask(packets)
        self.subspectrum_mask = self._get_subspectrum_mask(packets)
        self.compression_scheme_counts = self._get_compression_scheme(packets, 'NIXD0126',
                                                                      'NIXD0127', 'NIXD0128')
        subspec_data = {}
        j = 129
        for subspec, i in enumerate(range(300, 308)):
            subspec_data[subspec + 1] = {'num_points': packets.get(f'NIXD0{j}')[0],
                                         'num_summed_channel': packets.get(f'NIXD0{j + 1}')[0],
                                         'lowest_channel': packets.get(f'NIXD0{j + 2}')[0]}
            j += 3

        self.subspec_num_points = np.array([v['num_points'] for v in subspec_data.values()])
        self.subspec_num_summed_channel = np.array(
            [v['num_summed_channel'] for v in subspec_data.values()])
        self.subspec_lowest_channel = np.array(
            [v['lowest_channel'] for v in subspec_data.values()])

        subspec_index = np.argwhere(self.subspectrum_mask == 1)
        sub_channels = [np.arange(self.subspec_num_points[index] + 1) * (
                    self.subspec_num_summed_channel[index] + 1) + self.subspec_lowest_channel[index]
                        for index in subspec_index]
        channels = list(chain(*[ch.tolist() for ch in sub_channels]))
        self.num_channels = len(channels)

        # Data
        self.samples = np.array(packets.get('NIX00159'), np.uint16)
        self.num_samples = np.sum(self.samples)
        self.detector_id = np.array(packets.get('NIXD0155'), np.ubyte)
        self.pixel_id = np.array(packets.get('NIXD0156'), np.ubyte)
        self.subspec_id = np.array(packets.get('NIXD0157'), np.ubyte)
        self.num_spec_points = np.array(packets.get('NIX00146'), np.uint16)

        flat_counts = eng_packets.get('NIX00158')
        pos = 0
        counts = []
        for sp in self.num_spec_points:
            counts.append(flat_counts[pos:pos + sp])
            pos += sp

        self.num_detectors = np.sum(self.detector_mask) * np.sum(self.pixel_mask)
        self.spectra = np.concatenate(
            [counts[i * self.num_detectors:(i + 1) * self.num_detectors] for i in range(len(subspec_index))],
            axis=1)

    @staticmethod
    def _get_subspectrum_mask(packets):
        """
        Get subspectrum mask as bool array

        Parameters
        ----------
        packets : dict
            Merged packets

        Returns
        -------
        numpy.array
            Bool array of mask
        """
        subspectrum_masks = np.array([
            [bool(int(x)) for x in format(packets.get('NIX00160')[i], '08b')][::-1]
            for i in range(len(packets.get('NIX00160')))])

        if not np.all(subspectrum_masks == subspectrum_masks[0, :]):
            logger.warning(f'Detector mask changed in packet sequence')
        return subspectrum_masks[0]

    def to_hdul(self):
        """
        Create a CalibrationSpectra HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = calibration_spectra_fits(self.num_detectors, self.num_channels)

        # Control
        hdul[-1].data['DURATION'] = self.duration
        hdul[-1].data['QUIET_TIME'] = self.quiet_time
        hdul[-1].data['LIVE_TIME'] = self.live_time
        hdul[-1].data['AVERAGE_TEMP'] = self.average_temperature
        hdul[-1].data['COMPRESSION_SCHEME_ACCUM_SKM'] = self.compression_scheme_counts
        hdul[-1].data['DETECTOR_MASK'] = self.detector_mask
        hdul[-1].data['PIXEL_MASK'] = self.pixel_mask
        hdul[-1].data['SUBSPECTRUM_MASK'] = self.subspectrum_mask
        hdul[-1].data['SUBSPEC_ID'] = list(range(8))
        hdul[-1].data['SUBSPEC_NUM_POINTS'] = self.subspec_num_points
        hdul[-1].data['SUBSPEC_NUM_SUMMED_CHANNEL'] = self.subspec_num_summed_channel
        hdul[-1].data['SUBSPEC_LOWEST_CHANNEL'] = self.subspec_lowest_channel

        # Data
        hdul[1].data['DETECTOR_ID'] = self.detector_id[:self.num_detectors]
        hdul[1].data['PIXEL_ID'] = self.pixel_id[:self.num_detectors]
        hdul[1].data['SUBSPEC_ID'] = self.subspec_id[:self.num_detectors]
        hdul[1].data['NUM_POINTS'] = self.num_channels
        hdul[1].data['COUNTS'] = self.spectra

        return hdul


class FlareFlagAndLocation(BaseProduct):
    """
    Flare flag and location product
    """
    def __init__(self, packets):
        # HEADER
        super().__init__(packets)
        self.samples = packets.get('NIX00089')
        self.num_samples = sum(self.samples)

        self.obs_beg = scet_to_datetime(f'{self.scet_coarse[0]}:{self.scet_fine[0]}')
        self.obs_end = scet_to_datetime(f'{self.scet_coarse[-1]}:{self.scet_fine[-1]}')
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        self.time = self._get_time()

        # DATA
        self.loc_z = np.array(packets['NIX00283'], np.int8)
        self.loc_y = np.array(packets['NIX00284'], np.int8)
        self.thermal_index = np.array(packets['NIXD0061'], np.ubyte)
        self.non_thermal_index = np.array(packets['NIXD0060'], np.ubyte)
        self.location_status = np.array(packets['NIXD0059'], np.ubyte)

    def to_hdul(self):
        """
        Create a FlareFlagAndLocation HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        # Control
        hdul = flare_flag_location_fits(self.num_samples)
        hdul[-1].data['INTEGRATION_TIME'] = self.integration_time
        hdul[-1].data['NUM_SAMPLES'] = self.num_samples

        # Data
        hdul[1].data['THERMAL_INDEX'] = self.thermal_index
        hdul[1].data['NONTHERMAL_INDEX'] = self.non_thermal_index
        hdul[1].data['LOCATION_STATUS'] = self.location_status
        hdul[1].data['LOC_Z'] = self.loc_z
        hdul[1].data['LOC_Y'] = self.loc_y

        return hdul


class TMManagementAndFlareList:
    """
    TM Management and Flare list product.
    """
    def __init__(self, stix_packets):
        # Header
        self.ubsd_counter = stix_packets.get('NIX00285')[0]
        self.pald_counter = stix_packets.get('NIX00286')[0]
        self.num_flares = stix_packets.get('NIX00286')[0]

        # DATA
        self.start_scet_coarse = stix_packets.get('NIX00287')

        self.end_scet_coarse = stix_packets.get('NIX00287')
        self.obs_utc = scet_to_datetime(f'{self.start_scet_coarse:self.0}')
        self.highest_flareflag = stix_packets.get('NIX00289')[0]
        self.tm_byte_volume = stix_packets.get('NIX00290')[0]
        self.average_z_loc = stix_packets.get('NIX00291')[0]
        self.average_y_loc = stix_packets.get('NIX00292')[0]
        self.processing_mask = stix_packets.get('NIX00293')[0]

    def to_hdul(self):
        """
        Create a TMManagementAndFlareList HDUL.

        Returns
        -------
        astropy.io.fits.HUDList


        """
        hdul = tm_management_and_flare_list_fits(self.num_flares)

        # Control
        hdul[-1].data['UBSD_COUNTER'] = self.ubsd_counter
        hdul[-1].data['PALD_COUNTER'] = self.pald_counter
        hdul[-1].data['NUM_FLARES'] = self.num_flares

        # Data
        hdul[1].data['START_SCET_COARSE'] = self.start_scet_coarse
        hdul[1].data['END_SCET_COARSE'] = self.end_scet_coarse
        hdul[1].data['MAX_FLAG'] = self.highest_flareflag
        hdul[1].data['TM_VOL'] = self.tm_byte_volume
        hdul[1].data['AVG_Z_LOC'] = self.average_z_loc
        hdul[1].data['AVG_Y_LOC'] = self.average_y_loc
        hdul[1].data['PROCESSING_MASK'] = self.processing_mask


def get_energies_from_mask(mask=None):
    """
    Return energy channels for
    Parameters
    ----------
    mask : list or array
        Energy bin mask

    Returns
    -------
    tuple
        Lower and high energy edges
    """

    if mask is None:
        low = [ENERGY_CHANNELS[edge]['e_lower'] for edge in range(32)]
        high = [ENERGY_CHANNELS[edge]['e_upper'] for edge in range(32)]
    elif len(mask) == 33:
        edges = np.where(np.array(mask) == 1)[0]
        channel_edges = [edges[i:i+2].tolist() for i in range(len(edges)-1)]
        low = []
        high = []
        for edge in channel_edges:
            l, h = edge
            low.append(ENERGY_CHANNELS[l]['e_lower'])
            high.append(ENERGY_CHANNELS[h - 1]['e_upper'])
    elif len(mask) == 32:
        edges = np.where(np.array(mask) == 1)
        low_ind = np.min(edges)
        high_ind = np.max(edges)
        low = ENERGY_CHANNELS[low_ind]['e_lower']
        high = ENERGY_CHANNELS[high_ind]['e_upper']
    else:
        raise ValueError(f'Energy mask or edges must have a lenght of 32 or 33 not {len(mask)}')

    return low, high
