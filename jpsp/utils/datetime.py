import datetime as dt

import pytz as tz

""" 
datedict -> dict(
    date="2022-08-21",
    time="17:00:00",
    tz="Europe/Zurich"
)
"""


def datedict_to_utc_datetime(date: dict) -> dt.datetime:
    """ datedict to utc datetime """

    timezone = tz.timezone(date['tz'])

    date_val = date['date'][0:10]
    time_val = date['time'][0:8]

    # print(date_val, time_val)

    date_time_obj: dt.datetime = dt.datetime.strptime(
        f"{date_val} {time_val}",
        '%Y-%m-%d %H:%M:%S'
    )

    # print(date_time_obj)

    tz_date_time_obj: dt.datetime = timezone.localize(date_time_obj)

    utc_date_time_obj = tz_date_time_obj.astimezone(tz.utc)

    # print(date_time_obj)

    return utc_date_time_obj


def datedict_to_utc_str(date: dict) -> str:
    """ datetime dict to utc str """

    date_time_obj: dt.datetime = datedict_to_utc_datetime(date)
    return f"{date_time_obj}"


def datedict_to_utc_ts(date: dict) -> int:
    """ datetime dict to utc timestamp """

    date_time_obj: dt.datetime = datedict_to_utc_datetime(date)
    return int(round(date_time_obj.timestamp()))
