

from typing import Any, Callable, Generator


def split_list(lst, chunk_size) -> Generator[Any, Any, None]:
    for i in range(0, len(lst), chunk_size):
        yield lst[i:i+chunk_size]


def find(collection: list, predicate: Callable) -> Any | None:
    filtered = [c for c in collection if predicate(c) == True]
    return filtered[0] if filtered and len(filtered) > 0 else None
