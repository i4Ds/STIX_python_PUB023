from datetime import datetime

from stix_parser.datetime import scet_to_utc, utc_to_scet, datetime_to_scet, scet_to_datetime

T0_UTC_ISO = '2000-01-01T00:00:00.000'
T0_SCET = '1/0000000000:00000'
T0_DATETIME = datetime.fromisoformat(T0_UTC_ISO)

# Compare to know fixed SCET T0 value
def test_utc_to_scet_t0():
    assert utc_to_scet(T0_UTC_ISO) == T0_SCET

# Compare to know fixed UTC ISO T0 value
def test_scet_to_utc_t0():
    assert scet_to_utc(T0_SCET) == T0_UTC_ISO

#
def test_scet_to_utc_round_trips():
    now = datetime.now()
    now_str = now.isoformat(timespec='milliseconds')
    assert utc_to_scet(scet_to_utc(T0_SCET)) == T0_SCET
    assert scet_to_utc(utc_to_scet(T0_UTC_ISO)) == T0_UTC_ISO
    assert scet_to_utc(utc_to_scet(now_str)) == now_str

def test_scet_to_datetime_round_trips():
    now = datetime.now()
    # Only have 3 significant figures in milliseconds
    now_rounded = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second,
                           int(round(now.microsecond*10**-6,3)*10**6))
    assert scet_to_datetime(datetime_to_scet(T0_DATETIME)) == T0_DATETIME
    assert datetime_to_scet(scet_to_datetime(T0_SCET)) == T0_SCET
    assert scet_to_datetime(datetime_to_scet(now)) == now_rounded
