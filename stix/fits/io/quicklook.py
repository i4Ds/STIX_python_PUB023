""""
Quick Look fits file definitions
"""
from collections import defaultdict
from pathlib import Path

import numpy as np
from astropy.io import fits

from stix_parser.core import stix_datatypes as sdt
from stix_parser.datetime import datetime_to_scet
from stix_parser.products.science import XrayL0
from stix_parser.utils.logger import get_logger

logger = get_logger(__name__)


def energy_bands(num_energies):
    """
    Generate the energy band fits extension.

    Parameters
    ----------
    num_energies : int
        The number of energies

    Returns
    -------
    astropy.io.fits.BinTableHDU
        The Energy Extension

    """
    # Extension for energy channel data
    energy_columns = (
        fits.Column(name='CHANNEL', format='B', array=np.zeros(num_energies)),
        fits.Column(name='E_MIN', format='E', unit='KeV', array=np.zeros(num_energies)),
        fits.Column(name='E_MAX', format='E', unit='KeV', array=np.zeros(num_energies))
    )

    energy_coldefs = fits.ColDefs(energy_columns)
    enenrgy_hdu = fits.BinTableHDU.from_columns(energy_coldefs)
    enenrgy_hdu.name = 'ENEBAND'

    return enenrgy_hdu


def _create_hdul(control_hdu, data_columns, num_energies):
    data_coldefs = fits.ColDefs(data_columns)
    data_hdu = fits.BinTableHDU.from_columns(data_coldefs)
    data_hdu.name = 'RATE'
    energy_hdu = energy_bands(num_energies)
    primary = fits.PrimaryHDU()
    return fits.HDUList([primary, data_hdu, energy_hdu, control_hdu])


def light_curve_fits(num_samples, num_energies):
    """
     Generate light curve fits structures given number of samples (times) and number of energies.

    Parameters
    ----------
    num_samples : int
        Number of samples
    num_energies : int
        Number of energies

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    control_columns = (
            fits.Column(name='INTEGRATION_TIME', unit='0.1s', format='I'),
            fits.Column(name='DETECTOR_MASK', format='32B', array=np.zeros(1)),
            fits.Column(name='PIXEL_MASK', format='12B', array=np.zeros(1)),
            fits.Column(name='ENERGY_BIN_MASK', format='33B', array=np.zeros(1)),
            fits.Column(name='COMPRESSION_SCHEME_COUNTS_SKM', format='3I', array=np.zeros((1, 3))),
            fits.Column(name='COMPRESSION_SCHEME_TRIGGERS_SKM', format='3I', array=np.zeros((1, 3)))
        )

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='COUNTS', format=f'{num_energies}J',
                    array=np.zeros((num_samples, num_energies))),
        fits.Column(name='TRIGGERS',  format='J', array=np.zeros(num_samples)),
        fits.Column(name='RATE_CONTROL_REGIME', format='B', array=np.zeros(num_samples)),
        fits.Column(name='CHANNEL', format=f'{num_energies}B', array=np.zeros(num_samples)),
        fits.Column(name='TIME', format='D', array=np.zeros(num_samples)),
        fits.Column(name='TIMEDEL', format='E', array=np.zeros(num_samples)),
        fits.Column(name='LIVETIME', format='J', array=np.zeros(num_samples)),
        fits.Column(name='ERROR', format='J', array=np.zeros(num_samples))
    )

    light_curve_hdu_list = _create_hdul(control_hdu, data_columns, num_energies)
    return light_curve_hdu_list


def background_fits(num_samples, num_energies):
    """
    Generate background fits structures given number of samples (times) and number of energies.

    Parameters
    ----------
    num_samples : int
        Number of samples
    num_energies : int
        Number of energies

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    control_columns = (
        fits.Column(name='INTEGRATION_TIME', format='I'),
        fits.Column(name='ENERGY_BIN_MASK', format='33B', array=np.zeros(1)),
        fits.Column(name='COMPRESSION_SCHEME_BACKGROUND-SKM', format='3I', array=np.zeros((1, 3))),
        fits.Column(name='COMPRESSION_SCHEME_TRIGGERS-SKM', format='3I', array=np.zeros((1, 3)))
    )

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='COUNTS', format=f'{num_energies}J',
                    array=np.zeros((num_samples, num_energies))),
        fits.Column(name='TRIGGERS', format='J', array=np.zeros(num_samples)),
        fits.Column(name='CHANNEL', format=f'{num_energies}J', array=np.zeros(num_samples)),
        fits.Column(name='LIVETIME', format='I', array=np.zeros(num_samples)),
        fits.Column(name='ERROR', format='J', array=np.zeros(num_samples))
    )

    background_hdu_list = _create_hdul(control_hdu, data_columns, num_energies)
    return background_hdu_list


def spectra_fits(num_samples, num_energies):
    """
    Generate spectra fits structures given number of samples (times) and number of energies.

    Parameters
    ----------
    num_samples : int
        Number of samples
    num_energies : int
        Number of energies

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    control_columns = (
        fits.Column(name='INTEGRATION_TIME', format='I'),
        fits.Column(name='PIXEL_MASK', format='12B', array=np.zeros(1)),
        fits.Column(name='ENERGY_BIN_MASK', format='33B', array=np.zeros(1)),
        fits.Column(name='COMPRESSION_SCHEME_COUNTS-SKM', format='3I', array=np.zeros((1, 3))),
        fits.Column(name='COMPRESSION_SCHEME_TRIGGERS-SKM', format='3I', array=np.zeros((1, 3)))
    )

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='DETECTOR_INDEX', format='B'),
        fits.Column(name='COUNTS', format=f'{num_energies}J',
                    array=np.zeros((num_samples, num_energies))),
        fits.Column(name='TRIGGERS', format='J', array=np.zeros(num_samples)),
        fits.Column(name='CHANNEL', format=f'{num_energies}J', array=np.zeros(num_samples)),
        fits.Column(name='NUM_INTEGRATIONS', format='B'),
        fits.Column(name='TIME', format='D', array=np.zeros(num_samples)),
        fits.Column(name='TIMEDEL', format='E', array=np.zeros(num_samples)),
        fits.Column(name='LIVETIME', format='I', array=np.zeros(num_samples)),
        fits.Column(name='ERROR', format='J', array=np.zeros(num_samples))
    )

    spectra_hdu_list = _create_hdul(control_hdu, data_columns, num_energies)
    return spectra_hdu_list


def variance_fits(num_samples, num_energies):
    """
    Generate variance fits structures given number of samples (times) and number of energies.

    num_samples : int
        Number of samples
    num_energies : int
        Number of energies

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    control_columns = (
        fits.Column(name='INTEGRATION_TIME', format='I'),
        fits.Column(name='SAMPLES', format='I'),
        fits.Column(name='DETECTOR_MASK', format='32B', array=np.zeros(1)),
        fits.Column(name='PIXEL_MASK', format='12B', array=np.zeros(1)),
        fits.Column(name='ENERGY_BIN_MASK', format='32B', array=np.zeros(1)),
        fits.Column(name='COMPRESSION_SCHEME_VARIANCE-SKM', format='3I', array=np.zeros((1, 3))),
    )

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='VARIANCE', format=f'J',
                    array=np.zeros(num_samples)),
        fits.Column(name='CHANNEL', format=f'{num_energies}J', array=np.zeros(num_samples)),
        fits.Column(name='TIME', format='D', array=np.zeros(num_samples)),
        fits.Column(name='TIMEDEL', format='E', array=np.zeros(num_samples)),
        fits.Column(name='LIVETIME', format='I', array=np.zeros(num_samples)),
        fits.Column(name='ERROR', format='J', array=np.zeros(num_samples))
    )

    variance_hdu_list = _create_hdul(control_hdu, data_columns, num_energies)
    return variance_hdu_list


def flare_flag_location_fits(num_samples):
    """
    Generate flare flag and location fits structures given number of samples.

    Parameters
    ----------
    num_samples : `int`
        Number of flare flag and location data points

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    control_columns = [fits.Column(name='INTEGRATION_TIME', format='I'),
                       fits.Column(name='NUM_SAMPLES', format='I')]

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='THERMAL_INDEX', format='B', array=np.zeros(num_samples)),
        fits.Column(name='NONTHERMAL_INDEX', format='B', array=np.zeros(num_samples)),
        fits.Column(name='LOCATION_STATUS', format='B', array=np.zeros(num_samples)),
        fits.Column(name='LOC_Z', format='B', array=np.zeros(num_samples)),
        fits.Column(name='LOC_Y', format='B', array=np.zeros(num_samples))
    )

    data_coldefs = fits.ColDefs(data_columns)
    data_hdu = fits.BinTableHDU.from_columns(data_coldefs)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    flare_flag_location_hdu_list = fits.HDUList([primary, data_hdu, control_hdu])
    return flare_flag_location_hdu_list


def calibration_spectra_fits(num_structures, num_spec_points, spectra):
    """
    Generate calibration spectra fits structures given number of structures and spectral points.

    Parameters
    ----------
    num_structures : int
        Number of structures
    num_spec_points : int
        Number of spectral points
    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, control.
    """
    control_columns = [
        fits.Column(name='DURATION', format='J'),
        fits.Column(name='QUIET_TIME', format='I', array=np.zeros(1)),
        fits.Column(name='LIVE_TIME', format='I', array=np.zeros(1)),
        fits.Column(name='AVERAGE_TEMP', format='I', array=np.zeros(1)),
        fits.Column(name='COMPRESSION_SCHEME_ACCUM_SKM', format='3I', array=np.zeros((1, 3))),
        fits.Column(name='DETECTOR_MASK', format='32B', array=np.zeros(1)),
        fits.Column(name='PIXEL_MASK', format='12B', array=np.zeros(1)),
        fits.Column(name='SUBSPECTRUM_MASK', format='8B', array=np.zeros(1)),
    ]

    for i in range(1, 33):
        control_columns.append(fits.Column(name=f'SUBSPEC{i}_NUM_POINTS', format='I'))
        control_columns.append(fits.Column(name=f'SUBSPEC{i}_NUM_SUMMED', format='I'))
        control_columns.append(fits.Column(name=f'SUBSPEC{i}_LOW_CHAN', format='I'))

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='DETECTOR_ID', format='B', array=np.zeros(num_structures)),
        fits.Column(name='PIXEL_ID', format='B', array=np.zeros(num_structures)),
        fits.Column(name='SUBSPEC_ID', format='B', array=np.zeros(num_structures)),
        fits.Column(name='NUM_POINTS', format='I', array=np.zeros(num_structures)),
        fits.Column(name='COUNTS', format=f'PJ',
                    array=np.array(spectra, dtype=np.object_)),
    )

    data_coldefs = fits.ColDefs(data_columns)
    data_hdu = fits.BinTableHDU.from_columns(data_coldefs)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    calibration_spectra_hdu_list = fits.HDUList([primary, data_hdu, control_hdu])
    return calibration_spectra_hdu_list


def tm_management_and_flare_list_fits(num_samples):
    """
    Generate TM management and flare list fits structures given number of samples (flares).

    Parameters
    ----------
    num_samples : int
        Number of samples (flares)

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, control.
    """
    control_columns = (
        fits.Column(name='UBSD_COUNTER', format='J'),
        fits.Column(name='PALD_COUNTER', format='J'),
        fits.Column(name='NUM_FLARES', format='I')
    )

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='START_SCET_COARSE', format='J', array=np.zeros(num_samples)),
        fits.Column(name='END_SCET_COARSE', format='J', array=np.zeros(num_samples)),
        fits.Column(name='MAX_FLAG', format='B', array=np.zeros(num_samples)),
        fits.Column(name='TM_VOL', format='J', array=np.zeros(num_samples)),
        fits.Column(name='AVG_Z_LOC', format='B', array=np.zeros(num_samples)),
        fits.Column(name='AVG_Y_LOC', format='B', array=np.zeros(num_samples)),
        fits.Column(name='PROCESSING_MASK', format='B', array=np.zeros(num_samples))
    )

    data_coldefs = fits.ColDefs(data_columns)
    data_hdu = fits.BinTableHDU.from_columns(data_coldefs)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    flare_flag_location_hdu_list = fits.HDUList([primary, data_hdu, control_hdu])
    return flare_flag_location_hdu_list


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
    energybins = np.hstack([np.arange(16)+4, 20*(150/20)**(np.arange(16)/16), 150])
    if mask is None:
        return energybins[0:-1], energybins[1:]
    else:
        edges = np.where(mask == 1)[0]
        bins = np.array([edges[e:e + 2] for e in range(len(edges)-1)])

        return energybins[bins[:, 0]], energybins[bins[:, 1]]
