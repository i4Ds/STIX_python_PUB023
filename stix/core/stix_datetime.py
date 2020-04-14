#!/usr/bin/python3

import spiceypy
from . import config

from datetime import datetime
from dateutil import parser as dtparser


class SpiceManager:
    """taken from https://issues.cosmos.esa.int/solarorbiterwiki/display/SOSP/Translate+from+OBT+to+UTC+and+back
    """
    # SOLAR ORBITER naif identifier
    solar_orbiter_naif_id = -144

    __instance = None

    @staticmethod
    def get_instance():
        if not SpiceManager.__instance:
            SpiceManager()
        return SpiceManager.__instance

    def __init__(self):
        if SpiceManager.__instance:
            raise Exception('SpiceManager already initialized')
        else:
            SpiceManager.__instance = self
        tls_filename = config.spice['tls_filename']
        sclk_filename = config.spice['sclk_filename']
        spiceypy.furnsh(tls_filename)
        spiceypy.furnsh(sclk_filename)

    def obt2utc(self, obt_string):
        # Obt to Ephemeris time (seconds past J2000)
        ephemeris_time = spiceypy.scs2e(self.solar_orbiter_naif_id, obt_string)
        # Ephemeris time to Utc
        # Format of output epoch: ISOC (ISO Calendar format, UTC)
        # Digits of precision in fractional seconds: 3
        return spiceypy.et2utc(ephemeris_time, "ISOC", 3)

    def utc2obt(self, utc_string):
        # Utc to Ephemeris time (seconds past J2000)
        ephemeris_time = spiceypy.utc2et(utc_string)
        # Ephemeris time to Obt
        return ephemeris_time
        #return spiceypy.sce2s(self.solar_orbiter_naif_id,ephemeris_time)

    def scet2utc(self, coarse, fine=0):
        obt_string = '{}:{}'.format(coarse, fine)
        return self.obt2utc(obt_string)


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
            #it is a datetime str
        #    return '1970-01-01T00:00:00.000Z'
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
        utc = scet2utc(coarse, fine)
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


def utc2datetime(utc):
    if not utc.endswith('Z'):
        utc += 'Z'
    return dtparser.parse(utc)


if __name__ == '__main__':
    print("UTC at T0:")
    print(scet2utc(0))
    #print("Unix at T0:")
    #print(scet2unix(0))
    #print(scet2datetime(0))
