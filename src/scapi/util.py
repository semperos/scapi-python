import mimetypes
from copy import deepcopy
from typing import Any


def dissoc(dict: dict[Any, Any], key_to_remove: Any) -> dict[Any, Any]:
    """Return a copy of `dict` with `key_to_remove` absent."""
    d = deepcopy(dict)
    if key_to_remove in d:
        del d[key_to_remove]
    return d


def guess_mime_type(file_name: str) -> str:
    # mimetypes does not know about about Parquet
    if file_name.endswith(".parquet"):
        return "application/vnd.apache.parquet"
    (mime_type, _) = mimetypes.guess_type(file_name)
    return mime_type if mime_type is not None else "application/octet-stream"


def prefix_slash(s: str) -> str:
    if s.startswith("/"):
        return s
    return f"/{s}"
