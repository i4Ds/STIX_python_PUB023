#!/usr/bin/python3

import re
import glob
from datetime import datetime
from dateutil import parser as dtparser

import spiceypy
from stix.core import stix_logger
from stix.core import config

logger = stix_logger.get_logger()



# SOLAR ORBITER naif identifier
class SpiceManager:
    """taken from https://issues.cosmos.esa.int/solarorbiterwiki/display/SOSP/Translate+from+OBT+to+UTC+and+back
    """

    __instance = None

    @staticmethod
    def get_instance():
        if not SpiceManager.__instance:
            SpiceManager()
        return SpiceManager.__instance

    def __init__(self):
        if SpiceManager.__instance:
            raise Exception('Spice Manager already initialized')
        else:
            SpiceManager.__instance = self
        for pattern in config.get_spice():
            for fname in glob.glob(pattern):
                logger.info(f'loading spice data file: {fname}')
                spiceypy.furnsh(fname)

    def obt2utc(self, obt_string):
        # Obt to Ephemeris time (seconds past J2000)
        ephemeris_time = spiceypy.scs2e(-144, obt_string)
        # Ephemeris time to Utc
        # Format of output epoch: ISOC (ISO Calendar format, UTC)
        # Digits of precision in fractional seconds: 3
        return spiceypy.et2utc(ephemeris_time, "ISOC", 3)

    def utc2obt(self, utc_string):
        # Utc to Ephemeris time (seconds past J2000)
        ephemeris_time = spiceypy.utc2et(utc_string)
        # Ephemeris time to Obt
        #return ephemeris_time
        obt_string = spiceypy.sce2s(-144, ephemeris_time)
        time_fields = re.search('\/(.*?):(\d*)', obt_string)
        group = time_fields.groups()
        try:
            return int(group[0]) + int(group[1]) / 65536.
        except Exception as e:
            logger.warning(str(e))
            return 0

    def scet2utc(self, coarse, fine=0):
        obt_string = '{}:{}'.format(coarse, fine)
        print(obt_string)
        return self.obt2utc(obt_string)

    def utc2scet(self, utc):
        # Utc to Ephemeris time (seconds past J2000)
        ephemeris_time = spiceypy.utc2et(utc)
        # Ephemeris time to Obt
        return spiceypy.sce2s(-144, ephemeris_time)


spice_manager = SpiceManager.get_instance()


def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.isoformat(timespec='milliseconds')
    elif isinstance(dt, (int, float)):
        return datetime.utcfromtimestamp(dt).isoformat(timespec='milliseconds')
    elif isinstance(dt, str):
        try:
            return format_datetime(float(dt))
        except ValueError:
            return dt
    else:
        return '1970-01-01T00:00:00.000Z'


def get_now(dtype='unix'):
    utc_iso = datetime.utcnow().isoformat() + 'Z'
    if dtype == 'unix':
        return dtparser.parse(utc_iso).timestamp()
    return utc_iso


def scet2utc(coarse, fine=0):
    try:
        return spice_manager.scet2utc(coarse, fine)
    except spiceypy.utils.support_types.SpiceyError:
        return ''


def utc2scet(utc):
    return spice_manager.utc2obt(utc)


def utc2unix(utc):
    if isinstance(utc, str):
        if not utc.endswith('Z'):
            utc += 'Z'
        try:
            return dtparser.parse(utc).timestamp()
        except:
            return 0
    elif isinstance(utc, int) or isinstance(utc, float):
        return utc
    else:
        return 0


def unix2datetime(timestamp):
    dt = None
    if isinstance(timestamp, float):
        dt = datetime.utcfromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        try:
            ts = float(timestamp)
            dt = datetime.utcfromtimestamp(ts)
        except ValueError:
            dt = dtparser.parse(timestamp)
    elif isinstance(timestamp, datetime.datetime):
        dt = timestamp
    return dt


def datetime2unix(timestamp):
    dt = None
    if isinstance(timestamp, float):
        dt = datetime.utcfromtimestamp(timestamp)
    elif isinstance(timestamp, str):
        try:
            ts = float(timestamp)
            dt = datetime.utcfromtimestamp(ts)
        except ValueError:
            dt = dtparser.parse(timestamp)
    elif isinstance(timestamp, datetime.datetime):
        dt = timestamp
    if dt:
        return dt.timestamp()
    return 0


def scet2unix(coarse, fine=0):
    try:
        coarse_int = coarse
        fine_int = fine
        if isinstance(coarse, float):
            coarse_int = int(coarse)

        fine_int = int((coarse - coarse_int) * 65535)

        utc = scet2utc(coarse_int, fine_int)
        return utc2unix(utc)
    except spiceypy.utils.support_types.SpiceyError:
        return 0


def unix2utc(ts):
    return datetime.utcfromtimestamp(ts).isoformat(timespec='milliseconds')


def unix2scet(unix):
    utc = unix2utc(int(unix))
    return utc2scet(utc)


def scet2datetime(coarse, fine=0):
    unixtimestamp = scet2unix(coarse, fine)
    return datetime.utcfromtimestamp(unixtimestamp)


def unix2datetime(unix_timestamp):
    return datetime.utcfromtimestamp(unix_timestamp)


'''
    code taken from Shane's datetime script
'''


def utc2datetime(utc):
    if not utc.endswith('Z'):
        utc += 'Z'
    return dtparser.parse(utc)


def scet_to_utc(scet):
    return spice_manager.obt2utc(scet)


def scet_to_datetime(scet):
    utc_iso = scet_to_utc(scet)
    return dtparser.isoparse(utc_iso)


def utc_to_scet(utc):
    return spice_manager.utc2scet(utc)


def datetime_to_scet(dt):
    utc_iso = dt.isoformat(timespec='microseconds')
    scet = utc_to_scet(utc_iso)[2:]
    return scet


if __name__ == '__main__':
    print("UTC at T0:")
    print(scet2utc(0))
