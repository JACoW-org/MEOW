import datetime as dt
import pytz

from meow.models.application import Settings

start_date = dict(
    date="2022-08-21",
    time="17:00:00",
    tz="Europe/Zurich"
)

date_time_str = f"{start_date['date']} {start_date['time']}"
date_time_obj = dt.datetime.strptime(date_time_str, '%Y-%m-%d %H:%M:%S')

timezone = pytz.timezone(start_date['tz'])
tz_date_time_obj: dt.datetime = timezone.localize(date_time_obj)

utc_date_time_obj = tz_date_time_obj.astimezone(pytz.utc)

print("date_time_str", date_time_str)
print("tz_date_time_obj", tz_date_time_obj, tz_date_time_obj.tzinfo)
print("utc_date_time_obj", utc_date_time_obj, utc_date_time_obj.tzinfo)


# print(timezone_date_time_obj)
# print(start_date)


def dt_to_ts(val: dt.date) -> int:
    """ datetime -> unix timestamp """
    return int(round(val.astimezone(pytz.utc).timestamp()))


def dt_to_int(val: dt.date) -> int:
    """ datetime -> positional integer """

    return int(val.strftime("%Y%m%d%H%M%S"))


# dtime = dt.datetime.now()
# timezone = pytz.timezone("Asia/Kolkata")
# dtzone = timezone.localize(dtime)
#
# print("Time Zone: ", dtzone.tzinfo)
# print("Datetime: ", dtzone)
#
# print("Integer timestamp: ")
# print(dt_to_int(dtime))
# print(dt_to_int(dtzone))

# print(Settings.SearchIndex.dumps())
# print(Settings.SearchIndex.dumps())
# print(Settings.SearchIndex.dumps())
