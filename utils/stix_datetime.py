#!/usr/bin/python3
from datetime import datetime
from dateutil import parser as dtparser

SCET_OFFSET = 946684800.

#To be checked  2000-01-01T00:00.000Z
def format_datetime(dt):
    if isinstance(dt, datetime):
        return dt.isoformat(timespec='milliseconds')
    elif isinstance(dt, (int, float)):
        return datetime.utcfromtimestamp(dt).isoformat(timespec='milliseconds')
    elif isinstance(dt, str):
        try:
            return format_datetime(float(dt))
        except ValueError:
            return '1970-01-01T00:00.000Z'
    else:
        return '1970-01-01T00:00.000Z'


def convert_SCET_to_UTC(coarse_time, fine_time=0):
    unixtimestamp = coarse_time + fine_time / 65536. + SCET_OFFSET
    return convert_unixtimestamp_to_UTC(unixtimestamp)


def convert_UTC_to_unixtimestamp(utc):
    try:
        dtparser.parse(utc).timestamp()
    except:
        return 0


def convert_SCET_to_unixtimestamp(coarse_time, fine_time=0):
    return coarse_time + fine_time / 65536. + SCET_OFFSET


def convert_unixtimestamp_to_UTC(ts):
    return datetime.utcfromtimestamp(ts).isoformat(timespec='milliseconds')


def from_SCET(unix_timestamp):
    unixtimestamp = coarse_time + fine_time / 65536. + SCET_OFFSET
    return datetime.utcfromtimestamp(ts)


def from_unixtimestamp(unix_timestamp):
    return datetime.utcfromtimestamp(ts)


def from_UTC(utc):
    return dtparser.parse(utc)
