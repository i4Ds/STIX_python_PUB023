"""
Functions converting between on-board time (OBT) or spacecraft elapsed time (SCET) and UTC times.

References
----------
TBD

"""
import ftplib
from datetime import datetime
from urllib import request
from pathlib import Path
from dateutil import parser

import spiceypy

# Solar Obrbiter NAIF ID
SOLAR_ORBITER_NAIF_ID = -144

# TODO Maybe use pkg_resource or something

# Get root by definition of location of this file
ROOT = Path(__file__).parent.parent
SPACECRAFT_CLOCK_KERNEL = ROOT / 'data' / 'spice' / 'solo_ANC_soc-sclk_20000101_20160712_V01.tsc'
LEAP_SECONDS_KERNAL = ROOT / 'data' / 'spice' / 'naif0012.tls'


def _download_spice_kernels(overwrite=False):
    """
    Download spice kernels for time conversion.

    Parameters
    ----------
    overwrite : `boolean`
        Flag to overwrite current version of files

    Returns
    -------
    None

    """
    if not SPACECRAFT_CLOCK_KERNEL.exists() or overwrite is True:
        with request.urlopen('https://issues.cosmos.esa.int/solarorbiterwiki/download/attachments/'
                             '15926639/solo_ANC_soc-sclk_20000101_20160712_V01.tsc') as infile:
            with SPACECRAFT_CLOCK_KERNEL.open('wb') as outfile:
                outfile.write(infile.read())

    if not LEAP_SECONDS_KERNAL.exists() or overwrite is True:
        with ftplib.FTP('spiftp.esac.esa.int') as ftp:
            ftp.login()
            ftp.cwd('data/SPICE/SOLAR-ORBITER/kernels/lsk')
            with LEAP_SECONDS_KERNAL.open('wb') as file:
                ftp.retrbinary('RETR ' + LEAP_SECONDS_KERNAL.name, file.write)


_download_spice_kernels()

# Load kernel
spiceypy.furnsh(LEAP_SECONDS_KERNAL.as_posix())
spiceypy.furnsh(SPACECRAFT_CLOCK_KERNEL.as_posix())


def scet_to_utc(scet):
    """
    Convert SCET to UTC time strings in ISO format.

    Parameters
    ----------
    scet : `str`
        SCET time string e.g. 625237315:44104

    Returns
    -------
    `str`
        UTC time string in ISO format
    """
    # Obt to Ephemeris time (seconds past J2000)
    ephemeris_time = spiceypy.scs2e(SOLAR_ORBITER_NAIF_ID, scet)
    # Ephemeris time to Utc
    # Format of output epoch: ISOC (ISO Calendar format, UTC)
    # Digits of precision in fractional seconds: 6
    return spiceypy.et2utc(ephemeris_time, "ISOC", 3)


def utc_to_scet(utc):
    """
    Convert UTC ISO format to SCET time strings.

    Parameters
    ----------
    utc : str
        UTC time sring in is format e.g. '2019-10-24T13:06:46.682758'

    Returns
    -------
    str
        SCET time string
    """
    # Utc to Ephemeris time (seconds past J2000)
    ephemeris_time = spiceypy.utc2et(utc)
    # Ephemeris time to Obt
    return spiceypy.sce2s(SOLAR_ORBITER_NAIF_ID, ephemeris_time)


def scet_to_datetime(scet):
    """
    Convert SCET to datetime.

    Parameters
    ----------
    scet : str
        SCET time string e.g. 625237315:44104

    Returns
    -------
    datetime.datetime
        Datetime of SCET

    """
    utc_iso = scet_to_utc(scet)
    return parser.isoparse(utc_iso)


def datetime_to_scet(datetime):
    """
    Convert datetime to SCET.

    Parameters
    ----------
    datetime : datetime.datetime
        Time to convert to SCET

    Returns
    -------
    str
        SCET of datetime
    """
    utc_iso = datetime.isoformat(timespec='microseconds')
    scet = utc_to_scet(utc_iso)[2:]
    return scet
