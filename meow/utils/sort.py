
from typing import Any

from meow.utils.datetime import format_datetime_sec


def sort_list_by_date(val: Any) -> str:

    res = format_datetime_sec(val.start) \
        + '_' + val.code

    return res


def sort_list_by_code(val: Any) -> str:

    res = val.code

    return res


def sort_list_of_dict_code(val) -> str:

    res = val.get('code', '')

    return res


def sort_list_of_dict_by_date(val) -> str:

    res = format_datetime_sec(val.get('start', '')) \
        + '_' + val.get('code', '')

    return res


def sort_revision_list_by_date(val: Any) -> str:

    res = format_datetime_sec(val.creation_date) \
        + '_' + str(val.id)

    return res
