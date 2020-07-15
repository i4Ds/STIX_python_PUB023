"""
Science fits structures
"""
import numpy as np
from astropy.io import fits


def xray_l0_fits(num_structure, num_samples):
    """
    Generate X-ray L0 fits structures given number of structures and number of samples.

    Parameters
    ----------
    num_structure : int
        Number of structures
    num_samples : int
        Number of data samples

    Returns
    -------
    astropy.io.fits.HDUList
        HDU list, primary and binary extensions data, energy, control.
    """
    control_columns = [
        fits.Column(name='TC_PACKET_ID_REF', format='I'),
        fits.Column(name='TC_PACKET_SEQ_CONTROL', format='I'),
        fits.Column(name='REQUEST_ID', format='J'),
        fits.Column(name='COMPRESSION_SCHEME_COUNT_SKM', format='3I'),
        fits.Column(name='COMPRESSION_SCHEME_TRIGG_SKM', format='3I'),
        fits.Column(name='TIME_STAMP', format='K'),

        fits.Column(name='NUM_STRUCTURES', format='I'),
        fits.Column(name='START_TIME', format='I'),
        fits.Column(name='RCR', format='I'),
        fits.Column(name='INTEGRATION_DURATION', format='I'),
        fits.Column(name='PIXEL_MASK', format='I'),
        fits.Column(name='DETECTOR_MASK', format='J'),
    ]

    for i in range(16):
        control_columns.append(fits.Column(name=f'TRIGGERS_{i}', format='J'))

    control_coldefs = fits.ColDefs(control_columns)
    control_hdu = fits.BinTableHDU.from_columns(control_coldefs)
    control_hdu.name = 'CONTROL'

    data_columns = (
        fits.Column(name='NUM_SAMPLES', format='B'),
        fits.Column(name='PIXEL_ID', format='B', array=np.zeros(num_samples)),
        fits.Column(name='DETECTOR_ID', format='B', array=np.zeros(num_samples)),
        fits.Column(name='CHANNEL', format='B', array=np.zeros(num_samples)),
        fits.Column(name='CONTINUATION_BITS', format='B', array=np.zeros(num_samples)),
        fits.Column(name='COUNTS', format='I', array=np.zeros(num_samples))
    )

    data_coldefs = fits.ColDefs(data_columns)
    data_hdu = fits.BinTableHDU.from_columns(data_coldefs)
    data_hdu.name = 'RATE'

    primary = fits.PrimaryHDU()

    return fits.HDUList([primary, data_hdu, control_hdu])
