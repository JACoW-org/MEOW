
from typing import Any
from meow.utils.datetime import format_datetime_sec


def sort_list_by_date(val: Any):

    string = format_datetime_sec(val.start) \
        + '_' + val.code

    return string


def sort_list_by_code(val: Any):

    return val.code


def sort_list_of_dict_code(val):

    return val.get('code', '')


def sort_revision_list_by_date(val: Any):

    string = format_datetime_sec(val.creation_date) \
        + '_' + str(val.id)

    return string
