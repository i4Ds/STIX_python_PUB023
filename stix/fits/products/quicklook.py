"""
High level STIX data products created from single stand alone packets or a sequence of packects.
"""

import numpy as np

from datetime import timedelta

from stix_parser.datetime import scet_to_datetime
from stix_parser.io.fits.quicklook import light_curve_fits, flare_flag_location_fits, \
    get_energies_from_mask, background_fits, spectra_fits, variance_fits, \
    calibration_spectra_fits, tm_management_and_flare_list_fits
from stix_parser.utils.logger import get_logger

logger = get_logger(__name__)

__all__ = ['LightCurve', 'Background', 'Spectra', 'Variance', 'CalibrationSpectra',
           'FlareFlagAndLocation', 'TMManagementAndFlareList']


class BaseProduct:
    """
    Basic STIX data product.
    """
    def __init__(self, stix_packet):
        # Header
        self.scet_coarse = stix_packet['NIX00445'][0]
        self.scet_fine = stix_packet['NIX00446'][0]
        self.obs_utc = scet_to_datetime(f'{self.scet_coarse}:{self.scet_fine}')
        self.obs_beg = self.obs_utc
        self.integration_time = (stix_packet['NIX00405'][0] + 1) * 0.1  # Seconds
        self.obs_end = self.obs_beg + timedelta(seconds=self.integration_time)
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2


class LightCurve(BaseProduct):
    """
    Quick Look Light Curve data product.
    """
    def __init__(self, stix_packet):
        # Header
        super().__init__(stix_packet)
        # CONTROL
        self.detector_mask = stix_packet['NIX00407'][0]
        self.pixel_mask = stix_packet['NIXD0407'][0]
        self.energy_bin_mask = stix_packet['NIX00266'][0]
        self.energy_bin_mask_uppper = stix_packet['NIXD0107'][0]
        self.compression_scheme_counts = (stix_packet['NIXD0101'][0],
                                          stix_packet['NIXD0102'][0],
                                          stix_packet['NIXD0103'][0])
        self.compression_scheme_triggers = (stix_packet['NIXD0104'][0],
                                            stix_packet['NIXD0105'][0],
                                            stix_packet['NIXD0106'][0])
        # DATA

        self.num_energies = stix_packet['NIX00270'][0]
        # TODO Check why this is necessary
        samples = stix_packet['NIX00271'][::5]
        self.num_samples = sum(samples)
        counts = stix_packet['NIX00272']
        flat_indcies = np.cumsum([0, *samples])*self.num_energies
        arrays = []
        for i, sample in enumerate(samples):
            arrays.append(np.array(
                counts[flat_indcies[i]:flat_indcies[i+1]]).reshape(self.num_energies, sample))

        self.light_curves = np.concatenate(arrays, axis=1).T
        self.triggers = stix_packet['NIX00274'][0]
        self.rcr = stix_packet['NIX00276'][0]

    def to_hdul(self):
        """
        Create a LightCurve HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = light_curve_fits(self.num_samples, self.num_energies)

        # Control
        hdul[-1].data.INTEGRATION_TIME = self.integration_time
        hdul[-1].data.DETECTOR_MASK = np.array(
            [[np.array(d).astype(np.ubyte) for d in format(self.detector_mask, 'b').zfill(32)]])
        hdul[-1].data.PIXEL_MASK = np.array(
            [[np.array(d).astype(np.ubyte) for d in format(self.pixel_mask, 'b').zfill(12)]])
        full_energy_mask = format(self.energy_bin_mask, 'b').zfill(32) + format(
            self.energy_bin_mask_uppper, 'b')
        full_energy_mask = np.array([np.array(d).astype(np.ubyte) for d in
                                     full_energy_mask])
        hdul[-1].data.ENERGY_BIN_MASK = full_energy_mask
        hdul[-1].data.COMPRESSION_SCHEME_COUNTS_SKM = self.compression_scheme_counts
        hdul[-1].data.COMPRESSION_SCHEME_TRIGGERS_SKM = self.compression_scheme_counts

        # Data
        hdul[1].data.COUNTS = self.light_curves
        hdul[1].data.TRIGGERS = self.triggers
        hdul[1].data.RATE_CONTROL_REGIME = self.rcr

        hdul[1].header.update({'DATA_MAX': np.max(self.light_curves),
                               'DATA_MIN': np.min(self.light_curves),
                               'BUNIT': 'W m-2'})

        # Energy
        e_low, e_high = get_energies_from_mask(full_energy_mask)
        hdul[-2].data.E_MIN = e_low
        hdul[-2].data.E_MAX = e_high

        return hdul


class Background(BaseProduct):
    """
    Background product.
    """
    def __init__(self, stix_packet):
        # Header
        super().__init__(stix_packet)

        # Control
        self.energy_bin_edge_upper = stix_packet['NIXD0111'][0]
        self.energy_bin_edge_lower = stix_packet['NIX00266'][0]
        self.compression_scheme_background = (stix_packet['NIXD0108'][0],
                                              stix_packet['NIXD0109'][0],
                                              stix_packet['NIXD0109'][0])
        self.compression_scheme_triggers = (stix_packet['NIXD0112'][0],
                                            stix_packet['NIXD0113'][0],
                                            stix_packet['NIXD0114'][0])
        # Data
        self.num_energies = stix_packet.get('NIX00270')[0]
        samples = stix_packet['NIX00277'][::5]
        self.num_samples = sum(samples)
        counts = stix_packet['NIX00278']
        flat_indcies = np.cumsum([0, *samples]) * self.num_energies
        arrays = []
        for i, sample in enumerate(samples):
            arrays.append(
                np.array(counts[flat_indcies[i]:flat_indcies[i + 1]]).reshape(self.num_energies,
                                                                              sample))
        self.background = np.concatenate(arrays, axis=1).T
        self.triggers = stix_packet.get('NIX00274')

    def to_hdul(self):
        """
        Create a Background HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = background_fits(self.num_samples, self.num_energies)

        hdul[-1].data.INTEGRATION_TIME = self.integration_time

        full_energy_mask = format(self.energy_bin_edge_lower, 'b').zfill(32) + format(
            self.energy_bin_edge_upper, 'b')
        full_energy_mask = np.array([np.array(d).astype(np.ubyte) for d in
                                     full_energy_mask])
        hdul[-1].data.ENERGY_BIN_MASK = full_energy_mask

        hdul[-1].data.COMPRESSION_SCHEME_COUNTS_SKM = self.compression_scheme_background
        hdul[-1].data.COMPRESSION_SCHEME_TRIGGERS_SKM = self.compression_scheme_triggers

        hdul[1].data.COUNTS = self.background
        hdul[1].data.TRIGGERS = self.triggers

        e_low, e_high = get_energies_from_mask(full_energy_mask)
        hdul[-2].data.E_MIN = e_low
        hdul[-2].data.E_MAX = e_high

        return hdul


class Spectra(BaseProduct):
    """
    Background product.
    """
    def __init__(self, stix_packet):
        # Header
        super().__init__(stix_packet)

        # Control
        self.pixel_mask = stix_packet.get('NIXD0407')[0]
        self.compression_scheme_spectrum = (stix_packet['NIXD0115'][0],
                                            stix_packet['NIXD0116'][0],
                                            stix_packet['NIXD0117'][0])
        self.compression_scheme_triggers = (stix_packet['NIXD0112'][0],
                                            stix_packet['NIXD0113'][0],
                                            stix_packet['NIXD0114'][0])
        # Data
        self.num_samples = sum(stix_packet.get('NIX00089'))
        self.num_energies = 32
        self.detector_index = stix_packet.get('NIX00100')
        self.spectra = [stix_packet.get('NIX00{}'.format(i)) for i in range(452, 484)]
        self.triggers = stix_packet.get('NIX00484')
        self.num_integrations = stix_packet.get('NIX00485')

    def to_hdul(self):
        """
        Create a Spectra HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = spectra_fits(self.num_samples, self.num_energies)

        # Control
        hdul[-1].data.INTEGRATION_TIME = self.integration_time
        hdul[-1].data.PIXEL_MASK = format(self.pixel_mask, 'b').zfill(12)
        hdul[-1].data.COMPRESSION_SCHEME_COUNTS_SKM = self.compression_scheme_spectrum
        hdul[-1].data.COMPRESSION_SCHEME_TRIGGERS_SKM = self.compression_scheme_triggers

        # Data
        hdul[1].data.DETECTOR_INDEX = self.detector_index
        hdul[1].data.COUNTS = np.array(self.spectra).reshape(self.num_samples, self.num_energies)
        hdul[1].data.CHANNEL = np.array(range(32)).reshape(32, 1).repeat(self.num_samples, axis=1).T
        hdul[1].data.NUM_INTEGRATIONS = self.num_integrations

        # Energy
        e_low, e_high = get_energies_from_mask()
        hdul[-2].data.E_MIN = e_low
        hdul[-2].data.E_MAX = e_high

        return hdul


class Variance(BaseProduct):
    """
    Variance product.
    """
    def __init__(self, stix_packet):
        # Header
        super().__init__(stix_packet)

        # Control
        self.sample_per_variance = stix_packet.get('NIX00279')[0]
        self.detector_mask = stix_packet.get('NIX00407')[0]
        self.pixel_mask = stix_packet.get('NIXD0407')[0]
        self.energy_mask = stix_packet.get('NIX00282')[0]
        self.compression_scheme_variance = (stix_packet.get('NIXD0118')[0],
                                            stix_packet.get('NIXD0119')[0],
                                            stix_packet.get('NIXD0120')[0])

        # Data
        self.num_energies = 1
        self.num_samples = sum(stix_packet.get('NIX00280'))
        self.variance = stix_packet.get('NIX00281')

    def to_hdul(self):
        """
        Create a Variance HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = variance_fits(self.num_samples, self.num_energies)

        # Control
        hdul[-1].data.INTEGRATION_TIME = self.integration_time
        hdul[-1].data.SAMPLES = self.num_samples
        hdul[-1].data.PIXEL_MASK = np.array(
            [np.array(d).astype(np.ubyte) for d in format(self.pixel_mask, 'b').zfill(12)])
        hdul[-1].data.DETECTOR_MASK = np.array(
            [np.array(d).astype(np.ubyte) for d in format(self.detector_mask, 'b').zfill(32)])
        hdul[-1].data.ENERGY_MASK = np.array(
            [np.array(d).astype(np.ubyte) for d in format(self.energy_mask, 'b').zfill(32)])
        hdul[-1].data.COMPRESSION_SCHEME_VAROAMCE_SKM = self.compression_scheme_variance

        # Data
        hdul[1].data.VARIANCE = np.array(self.variance)

        # Energy
        e_low, e_high = get_energies_from_mask(hdul[-1].data.ENERGY_MASK)
        hdul[-2].data.E_MIN = e_low[0]
        hdul[-2].data.E_MAX = e_high[-1]

        return hdul


class CalibrationSpectra:
    """
    Calibration Specta data product.
    """
    def __init__(self, stix_packet):
        # Header
        self.scet_coarse = stix_packet['NIX00445'][0]
        self.scet_fine = 0
        self.obs_utc = scet_to_datetime(f'{self.scet_coarse}:{self.scet_fine}')
        self.duration = stix_packet['NIX00122'][0]
        self.obs_beg = self.obs_utc
        self.obs_end = self.obs_beg + timedelta(seconds=self.duration)
        self.obs_avg = self.obs_beg + (self.obs_end - self.obs_beg) / 2

        # Control
        self.quiet_time = stix_packet.get('NIX00123')[0]
        self.live_time = stix_packet.get('NIX00124')[0]
        self.average_temperature = stix_packet.get('NIX00125')[0]
        self.detector_mask = stix_packet.get('NIX00407')[0]
        self.pixel_mask = stix_packet.get('NIXD0407')[0]
        self.subspectrum_mask = stix_packet.get('NIX00160')[0]
        self.compression_scheme_counts = (stix_packet.get('NIXD0126')[0],
                                          stix_packet.get('NIXD0127')[0],
                                          stix_packet.get('NIXD0128')[0])
        self.subspec_data = {}
        j = 129
        for subspec, i in enumerate(range(300, 308)):
            self.subspec_data[subspec + 1] = {'num_points': stix_packet.get(f'NIXD0{j}')[0],
                                              'num_summed_channel':
                                                  stix_packet.get(f'NIXD0{j + 1}')[0],
                                              'lowest_channel': stix_packet.get(f'NIXD0{j + 2}')[0]}
            j += 3

        # Data
        self.num_structures = sum(stix_packet.get('NIX00159'))
        self.detector_id = stix_packet.get('NIXD0155')
        self.pixel_id = stix_packet.get('NIXD0156')
        self.subspec_id = stix_packet.get('NIXD0157')
        self.num_spec_points = stix_packet.get('NIX00146')

        flat_counts = stix_packet.get('NIX00158')
        pos = 0
        counts = []
        for sp in self.num_spec_points:
            counts.append(flat_counts[pos:pos + sp])
            pos += sp

        self.spectra = counts

    def to_hdul(self):
        """
        Create a CalibrationSpectra HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        hdul = calibration_spectra_fits(self.num_structures, self.num_spec_points, self.spectra)

        # Control
        hdul[-1].data.DURATION = self.duration
        hdul[-1].data.QUIET_TIME = self.quiet_time
        hdul[-1].data.LIVE_TIME = self.live_time
        hdul[-1].data.AVERAGE_TEMP = self.average_temperature
        hdul[-1].data.COMPRESSION_SCHEME_ACCUM_SKM = self.compression_scheme_counts
        hdul[-1].data.DETECTOR_MASK = np.array(
            [np.array(d).astype(np.ubyte) for d in format(self.detector_mask, 'b').zfill(32)])
        hdul[-1].data.PIXEL_MASK = np.array(
            [np.array(d).astype(np.ubyte) for d in format(self.pixel_mask, 'b').zfill(12)])
        hdul[-1].data.SUBSPECTRUM_MASK = np.array(
            [np.array(d).astype(np.ubyte) for d in format(self.subspectrum_mask, 'b').zfill(8)])
        for k, v in self.subspec_data.items():
            hdul[-1].data[f'SUBSPEC{k}_NUM_POINTS'] = v['num_points']
            hdul[-1].data[f'SUBSPEC{k}_NUM_SUMMED'] = v['num_summed_channel']
            hdul[-1].data[f'SUBSPEC{k}_LOW_CHAN'] = v['lowest_channel']

        # Data
        hdul[1].data.DETECTOR_ID = self.detector_id
        hdul[1].data.PIXEL_ID = self.pixel_id
        hdul[1].data.SUBSPEC_ID = self.subspec_id
        hdul[1].data.NUM_POINTS = self.num_spec_points

        return hdul


class FlareFlagAndLocation(BaseProduct):
    """
    Flare flag and location product
    """
    def __init__(self, stix_packet):
        # HEADER
        super().__init__(stix_packet)
        self.num_samples = stix_packet['NIX00089'][0]

        # DATA
        self.loc_z = stix_packet['NIX00283']
        self.loc_y = stix_packet['NIX00284']
        self.thermal_index = stix_packet['NIXD0061']
        self.non_thermal_index = stix_packet['NIXD0060']
        self.location_status = stix_packet['NIXD0059']

    def to_hdul(self):
        """
        Create a FlareFlagAndLocation HDUL.

        Returns
        -------
        astropy.io.fits.HUDList

        """
        # Control
        # TODO remove once issue with num_samples resolved
        hdul = flare_flag_location_fits(len(self.thermal_index))
        hdul[-1].data.INTEGRATION_TIME = self.integration_time
        hdul[-1].data.NUM_SAMPLES = self.num_samples

        # Data
        hdul[1].data.THERMAL_INDEX = self.thermal_index
        hdul[1].data.NONTHERMAL_INDEX = self.non_thermal_index
        hdul[1].data.LOCATION_STATUS = self.location_status
        hdul[1].data.LOC_Z = self.loc_z
        hdul[1].data.LOC_Y = self.loc_y

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
        hdul[-1].data.UBSD_COUNTER = self.ubsd_counter
        hdul[-1].data.PALD_COUNTER = self.pald_counter
        hdul[-1].data.NUM_FLARES = self.num_flares

        # Data
        hdul[1].data.START_SCET_COARSE = self.start_scet_coarse
        hdul[1].data.END_SCET_COARSE = self.end_scet_coarse
        hdul[1].data.MAX_FLAG = self.highest_flareflag
        hdul[1].data.TM_VOL = self.tm_byte_volume
        hdul[1].data.AVG_Z_LOC = self.average_z_loc
        hdul[1].data.AVG_Y_LOC = self.average_y_loc
        hdul[1].data.PROCESSING_MASK = self.processing_mask
