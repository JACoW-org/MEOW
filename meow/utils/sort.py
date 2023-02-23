
from typing import Any
from meow.utils.datetime import  format_datetime_sec


def sort_list_by_date(val: Any):

    string = format_datetime_sec(val.start) \
        + '_' + val.code

    return string
