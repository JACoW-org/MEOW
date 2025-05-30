import traceback
from typing import Optional


def exception_to_string(ex: Optional[BaseException]) -> dict | None:
    if not ex:
        return None

    stack = traceback.extract_stack()[:-3] + traceback.extract_tb(ex.__traceback__)  # add limit=??
    pretty = traceback.format_list(stack)

    return dict(
        message='{}'.format(ex),
        class_name=type(ex).__name__,
        stack_trace=''.join(pretty)
    )
