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
            return dt
            #it is a datetime str
        #    return '1970-01-01T00:00:00.000Z'
    else:
        return '1970-01-01T00:00:00.000Z'

def convert_SCET_to_UTC(coarse_time, fine_time=0):
    unixtimestamp = coarse_time + fine_time / 65536. + SCET_OFFSET
    return convert_unixtimestamp_to_UTC(unixtimestamp)


def convert_UTC_to_unixtimestamp(utc):
    if isinstance(utc, str):
        if not utc.endswith('Z'):
            utc += 'Z'
        try:
            dtparser.parse(utc).timestamp()
        except:
            return 0
    else:
        return utc


def convert_to_datetime(timestamp):
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


def convert_to_timestamp(timestamp):
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
    if not utc.endswith('Z'):
        utc += 'Z'
    return dtparser.parse(utc)
