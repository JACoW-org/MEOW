import datetime as dt

import pytz as tz

"""
datedict -> dict(
    date="2022-08-21",
    time="17:00:00",
    tz="Europe/Zurich"
)
"""


def format_datetime_sec(d: dt.datetime | None) -> str:
    return str(d.timestamp()) if d else ''


def format_datetime_day(d: dt.datetime | None) -> str:
    return d.strftime('%-j') if d else ''


def format_datetime_full(d: dt.datetime | None) -> str:
    return d.strftime('%d %B %Y %H:%M') if d else ''


def format_datetime_time(d: dt.datetime | None) -> str:
    return d.strftime('%H:%M') if d else ''


def format_datetime_dashed(d: dt.datetime | None) -> str:
    return d.strftime('%Y-%m-%d') if d else ''


def format_datetime_year_num(d: dt.datetime | None) -> str:
    return d.strftime('%Y') if d else ''


def format_datetime_month_name(d: dt.datetime | None) -> str:
    return d.strftime('%b') if d else ''


def format_datetime_pdf(d: dt.datetime) -> str:
    # D:YYYYMMDDHHmmSSOHH'mm'
    utc_offset = d.strftime('%z')
    return d.strftime(f"D:%Y%m%d%H%M%S{utc_offset[0:3]}'{utc_offset[3:]}'")


def format_datetime_doi(d: dt.datetime | None) -> str:
    return d.strftime("%d %B %Y") if d else ''


def format_datetime_doi_iso(d: dt.datetime | None) -> str:
    return d.strftime("%Y%m%d%H%M%S") if d else ''


def format_datetime_range(start: dt.datetime, end: dt.datetime) -> str:

    if start is None or end is None:
        return ''

    def _format_datetime_range_same_day(s: dt.datetime, e: dt.datetime) -> str:
        return f"{format_datetime_full(start)} - {format_datetime_time(end)}"

    def _format_datetime_range_different_day(s: dt.datetime, e: dt.datetime) -> str:
        return f"{format_datetime_full(start)} - {format_datetime_full(end)}"

    return _format_datetime_range_same_day(start, end) \
        if format_datetime_day(start) == format_datetime_day(end) \
        else _format_datetime_range_different_day(start, end)


def format_datetime_range_doi(start: dt.datetime, end: dt.datetime) -> str:
    """ """

    if start is None or end is None:
        return ''

    # same day
    if start == end:
        return start.strftime('%d %b %Y')

    # same year
    if start.year == end.year:
        # same month
        if start.month == end.month:
            return f'{start.strftime("%d")}-{end.strftime("%d %b %Y")}'
        # different month
        else:
            return f'{start.strftime("%d %b")}-{end.strftime("%d %b %Y")}'

    return f'{start.strftime("%d %b %Y")}-{end.strftime("%d %b %Y")}'


def datedict_to_tz_datetime(date: dict | None) -> dt.datetime:
    """ datedict to utc datetime """

    if date:

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

        return tz_date_time_obj

    print('datedict_to_tz_datetime -->')
    print(date)

    raise Exception('Invalid date dict')


def datedict_to_utc_datetime(date: dict | None) -> dt.datetime:
    """ datedict to utc datetime """

    if date:

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

    raise Exception('Invalid date dict')


def datedict_to_utc_str(date: dict | None) -> str | None:
    """ datetime dict to utc str """

    date_time_obj: dt.datetime | None = datedict_to_utc_datetime(date)

    return f"{date_time_obj}" if date_time_obj else None


def datedict_to_utc_ts(date: dict | None) -> int | None:
    """ datetime dict to utc timestamp """

    date_time_obj: dt.datetime | None = datedict_to_utc_datetime(date)

    return int(round(date_time_obj.timestamp())) if date_time_obj else None
