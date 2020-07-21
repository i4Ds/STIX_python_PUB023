"""
Science fits structures
"""
import numpy as np
from astropy.io import fits

from stix.fits.io.quicklook import energy_bands


COMMON_CONTROL_COLS = [
    fits.Column(name='TC_PACKET_ID_REF', format='I', bzero=2**15),
    fits.Column(name='TC_PACKET_SEQ_CONTROL', format='I', bzero=2**15),
    fits.Column(name='REQUEST_ID', format='J', bzero=2**31),
    fits.Column(name='COMPRESSION_SCHEME_COUNT_SKM', format='3B'),
    fits.Column(name='COMPRESSION_SCHEME_TRIGG_SKM', format='3B'),
    fits.Column(name='TIME_STAMP', format='K', array=np.zeros(1)),
    fits.Column(name='NUM_STRUCTURES', format='I', bzero=2**15, array=np.zeros(1))
]


def xray_l0_fits(num_structures, num_samples, num_times, num_energies, num_pixels):
    """
    Generate X-ray L0 fits structures given number of structures and number of samples.

    Parameters
    ----------
    num_structures : int
        Number of structures
    num_samples : int
        Number of data samples

    Returns
    -------
    `astropy.io.fits.HDUList`
        HDU list, primary and binary extensions data, energy, control.
    """
    energy_hdu = energy_bands(32)

    control_columns = COMMON_CONTROL_COLS[:]
    control_columns.extend([
        fits.Column(name='RCR', format='B', array=np.zeros(num_structures)),
        fits.Column(name='INTEGRATION_DURATION', format='E', array=np.zeros(num_structures)),
        fits.Column(name='PIXEL_MASK', format='12B', array=np.zeros((num_structures, 12))),
        fits.Column(name='DETECTOR_MASK', format='32B', array=np.zeros((num_structures, 32))),
        fits.Column(name='NUM_SAMPLES', format='J', bzero=2**15),
        fits.Column(name=f'TRIGGERS', format='16J', bzero=2**31,
                    array=np.zeros((num_structures, 16)))
    ])
    control_hdu = fits.BinTableHDU.from_columns(control_columns)
    control_hdu.name = 'CONTROL'

    num = num_times * num_energies

    raw_data_columns = (
        fits.Column(name='RAW_TIME', format='E', unit='s', array=np.zeros(num_samples)),
        fits.Column(name='PIXEL_ID', format='B', array=np.zeros(num_samples)),
        fits.Column(name='DETECTOR_ID', format='B', array=np.zeros(num_samples)),
        fits.Column(name='CHANNEL', format='B', array=np.zeros(num_samples)),
        fits.Column(name='CONTINUATION_BITS', format='B', array=np.zeros(num_samples)),
        fits.Column(name='RAW_COUNTS', format='I', bzero=2**15, array=np.zeros(num_samples)),
    )
    raw_data_hdu = fits.BinTableHDU.from_columns(raw_data_columns)
    raw_data_hdu.name = 'RAW_RATE'

    data_columns = (
        fits.Column(name='TIME', format='E', unit='s',array=np.zeros(num)),
        fits.Column(name='COUNTS', format=f'{num_energies*num_pixels}I',
                    bzero=2**15, dim=f'({num_pixels}, {num_energies})',
                    array=np.zeros((num, num_energies*num_pixels)))
    )
    data_hdu = fits.BinTableHDU.from_columns(data_columns)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    return fits.HDUList([primary, raw_data_hdu, data_hdu, energy_hdu, control_hdu])


def xray_l1l2_fits(num_strutures, num_detectors, num_energies, num_pixel_sets, num_records):
    """
    Generate X-ray L1 fits structures

    Parameters
    ----------

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    energy_hdu = energy_bands(32)

    control_columns = COMMON_CONTROL_COLS[:]
    control_columns.extend([
        fits.Column(name='DELTA_TIME', format='E', unit='s'),
        fits.Column(name='RCR', format='B', array=np.zeros(num_strutures)),
        fits.Column(name='DURATION', format='E', unit='s',
                    array=np.zeros(num_strutures)),
        fits.Column(name='NUM_PIXEL_SET', format=f'B', array=np.zeros(1)),
        fits.Column(name='PIXEL_MASKS', format=f'{12*num_pixel_sets}B',
                    dim=f'(12, {num_pixel_sets})', array=np.zeros((num_strutures, 12*num_pixel_sets))),
        fits.Column(name='DETECTOR_MASKS', format='32B',
                    array=np.zeros(num_strutures)),
        fits.Column(name='TRIGGERS', format='16J', bzero=2**31, array=np.zeros((num_strutures, 16))),
        fits.Column(name='NUM_ENERGY_GROUPS', format='B', array=np.zeros(num_strutures))
    ])
    control_hdu = fits.BinTableHDU.from_columns(control_columns)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='TIME', format='E', unit='s'),
        fits.Column(name='E_LOW', format=f'{num_energies}B', array=np.zeros(num_records)),
        fits.Column(name='E_HIGH', format=f'{num_energies}B', array=np.zeros(num_records)),
        fits.Column(name='NUM_DATA_ELEMENTS', format=f'{num_energies}I', bzero=2**15,
                    array=np.zeros(num_records)),
        fits.Column(name='COUNTS', format=f'{num_energies*num_pixel_sets}I',
                    dim=f'({num_pixel_sets}, {num_energies})', bzero=2**15,
                    array=np.zeros((num_records, num_energies, num_pixel_sets)))
    )
    data_hdu = fits.BinTableHDU.from_columns(data_columns)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    return fits.HDUList([primary, data_hdu, energy_hdu, control_hdu])


def xray_l3_fits(num_structures, num_energy_groups, num_detectors):
    """
    Generate X-ray L3 fits structures

    Parameters
    ----------

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    energy_hdu = energy_bands(32)

    control_columns = COMMON_CONTROL_COLS[:]
    control_columns.extend([
        fits.Column(name='DELTA_TIME', format='I', array=np.zeros(num_structures)),
        fits.Column(name='RCR', format='I', array=np.zeros(num_structures)),
        fits.Column(name='INTEGRATION_DURATION', format='I', array=np.zeros(1)),
        fits.Column(name='PIXEL_MASK1', format='12B', array=np.zeros(num_structures)),
        fits.Column(name='PIXEL_MASK2', format='12B', array=np.zeros(num_structures)),
        fits.Column(name='PIXEL_MASK3', format='12B', array=np.zeros(num_structures)),
        fits.Column(name='PIXEL_MASK4', format='12B', array=np.zeros(num_structures)),
        fits.Column(name='PIXEL_MASK5', format='12B', array=np.zeros(num_structures)),
        fits.Column(name='DETECTOR_MASKS', format='32B', array=np.zeros(num_structures)),
        fits.Column(name='TRIGGERS', format='16I', array=np.zeros((num_structures, 16))),
        fits.Column(name='NUM_ENERGY_GROUPS', format='I', array=np.zeros(1))
    ])
    control_hdu = fits.BinTableHDU.from_columns(control_columns)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='TIME', format='E', array=np.zeros(num_energy_groups)),
        fits.Column(name='E_LOW', format='I', array=np.zeros(num_energy_groups)),
        fits.Column(name='E_HIGH', format='I', array=np.zeros(num_energy_groups)),
        fits.Column(name='FLUX', format='I', array=np.zeros(num_energy_groups)),
        fits.Column(name='DETECTOR_ID', format=f'{num_detectors}B',
                    array=np.zeros((num_energy_groups, num_detectors))),
        fits.Column(name='VISIBILITY', format=f'{num_detectors}C',
                    array=np.zeros((num_energy_groups, num_detectors)))
    )
    data_hdu = fits.BinTableHDU.from_columns(data_columns)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    return fits.HDUList([primary, data_hdu, energy_hdu, control_hdu])


def xray_spectrogram(num_structures, num_times, num_energies):
    energy_hdu = energy_bands(num_energies)

    control_columns = COMMON_CONTROL_COLS[:]
    control_columns.extend([
        fits.Column(name='PIXEL_MASK', format='12B', array=np.zeros(num_structures)),
        fits.Column(name='DETECTOR_MASK', format='32B', array=np.zeros(num_structures)),
        fits.Column(name='RCR', format='B', array=np.zeros(num_structures)),
        fits.Column(name='E_MIN', format='B', array=np.zeros(num_structures)),
        fits.Column(name='E_MAX', format='B', array=np.zeros(num_structures)),
        fits.Column(name='E_BIN_WIDTH', format='B', array=np.zeros(num_structures))
    ])
    control_hdu = fits.BinTableHDU.from_columns(control_columns)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='TIME', format='E', array=np.zeros(num_times)),
        fits.Column(name='DELTA_TIME', format='E', array=np.zeros(num_times)),
        fits.Column(name='COMBINED_TRIGGERS', format='J', array=np.zeros(num_times)),
        fits.Column(name='COUNTS', format=f'{num_energies}J',
                    array=np.zeros((num_times, num_energies))),
        fits.Column(name='CLOSE_TIME_OFFSET', format='E', array=np.zeros(num_times))
    )
    data_hdu = fits.BinTableHDU.from_columns(data_columns)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    return fits.HDUList([primary, data_hdu, energy_hdu, control_hdu])


def aspect(num_samples):
    """
    Generate Aspect fits structures given number of samples.

    Parameters
    ----------
    num_samples : int
        Number of data samples

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    control_columns = [
        fits.Column(name='SUMMING_VALUE', format='B', array=np.zeros(1)),
        fits.Column(name='NUM_SAMPLES', format='J', array=np.zeros(1)),
    ]

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='TIME', format='E', unit='s', array=np.zeros(num_samples)),
        fits.Column(name='CHA_DIODE0', format='I', array=np.zeros(num_samples)),
        fits.Column(name='CHA_DIODE1', format='I', array=np.zeros(num_samples)),
        fits.Column(name='CHB_DIODE0', format='I', array=np.zeros(num_samples)),
        fits.Column(name='CHB_DIODE1', format='I', array=np.zeros(num_samples))
    )

    data_coldefs = fits.ColDefs(data_columns)
    data_hdu = fits.BinTableHDU.from_columns(data_coldefs)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    return fits.HDUList([primary, data_hdu, control_hdu])
