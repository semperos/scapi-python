"""
Simple API client for Shortcut's v3 REST API
"""

import logging
import os
import sys
from abc import ABC, abstractmethod
from collections.abc import Callable, Mapping, Sequence
from io import FileIO
from typing import Any, NamedTuple, NoReturn, Self, TypeAlias

import requests
from pyrate_limiter import Duration, InMemoryBucket, Limiter, Rate

from scapi.util import dissoc, guess_mime_type, prefix_slash

_url_base = "https://api.app.shortcut.com/api/v3"
_headers: dict[str, str] = {
    "Accept": "application/json; charset=utf-8",
    "Content-Type": "application/json",
    "User-Agent": "scapi/0.0.1",
}
_token: str | None = os.getenv("SHORTCUT_API_TOKEN")

# Rate Limiting
#
# https://developer.shortcut.com/api/rest/v3#Rate-Limiting
#
# The Shortcut API limit is 200 per minute; the 200th request within 60 seconds
# will receive an HTTP 429 response.
#
# The rate limiting config below sets an in-memory limit that is just below
# Shortcut's rate limit to reduce the possibility of being throttled, and sets
# the amount of time it will wait once it reaches that limit to just
# over a minute to account for possible computer clock differences.
_max_requests_per_minute = 200
_rate: Rate = Rate(_max_requests_per_minute, Duration.MINUTE)
_bucket: InMemoryBucket = InMemoryBucket([_rate])
_bucket_name = "shortcut-api-request"
_max_limiter_delay_seconds = 70
_limiter: Limiter = Limiter(
    _bucket,
    raise_when_fail=True,
    max_delay=Duration.SECOND * _max_limiter_delay_seconds,
)


class FileUploads(NamedTuple):
    responses: list[requests.Response]
    succeeded: list[dict[str, Any]]
    failed: list[str]


def exit_fail() -> NoReturn:
    sys.exit(1)


# From _typeshed:
# Marker for return types that include None, but where forcing the user to
# check for None can be detrimental. Sometimes called "the Any trick".
MaybeNone: TypeAlias = Any


class Formatter(ABC):
    """
    Class for formatting responses from Shortcut's API.

    This library has optional extras that support transforming Shortcut's JSON
    responses into different formats (e.g., Parquet). This class supports
    a common interface that these extras can implement.
    """

    @abstractmethod
    def object(self, response: requests.Response) -> Any:
        """
        Return an object representation of the response.
        """
        ...

    @abstractmethod
    def string(self, response: requests.Response) -> str:
        """
        Format the response from Shortcut, returning it as a string.
        """
        ...

    @abstractmethod
    def write(self, file: FileIO, response: requests.Response) -> Any:
        """
        Format the response from Shortcut, writing it to the file,
        returning True if everything was written successfully.
        """
        ...


class ResponseFormatter(Formatter):
    def object(self, response: requests.Response) -> Any:
        return response

    def string(self, response: requests.Response) -> str:
        return response.text

    def write(self, file: FileIO, response: requests.Response) -> Any:
        return file.write(str.encode(self.string(response)))


class JsonFormatter(Formatter):
    def object(self, response: requests.Response) -> Any:
        return response.json()

    def string(self, response: requests.Response) -> str:
        return response.text

    def write(self, file: FileIO, response: requests.Response) -> Any:
        # Shortcut v3 responses are always JSON
        return file.write(str.encode(response.text))


_formatter = ResponseFormatter()


class ShortcutClient:
    formatter: Formatter
    limiter: Limiter
    logger: logging.Logger
    token: str | None

    def __init__(
        self,
        token: str | None = _token,
        limiter: Limiter = _limiter,
        formatter: Formatter = _formatter,
    ):
        self.formatter = formatter
        self.limiter = limiter
        self.logger = logging.getLogger(__name__)
        self.token = token

    # From https://docs.python-requests.org/en/latest/api/
    def debug(self) -> None:
        # Enabling debugging at http.client level (requests->urllib3->http.client)
        # you will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
        # the only thing missing will be the response.body which is not logged.
        from http.client import HTTPConnection

        HTTPConnection.debuglevel = 1

        logging.basicConfig()  # you need to initialize logging, otherwise you will not see anything from requests
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def validate(
        self,
        exit_callback: Callable[[], Any] = exit_fail,
    ) -> Self | NoReturn:
        problems: list[str] = []
        if self.token is None:
            problems.append(
                " - You must provide a Shortcut API token. Either pass one to the ShortcutClient constructor or define a SHORTCUT_API_TOKEN environment."
            )
        if problems:
            msg = "\n".join(problems)
            self.logger.error(f"ShortcutClient did not validate:\n{msg}")
            exit_callback()
        return self

    def get(
        self, path: str, params: Mapping[str, str] | None = {}
    ) -> requests.Response:
        """
        Make an HTTP GET call to Shortcut's API.

        Serializes params as url query parameters.
        """
        self.limiter.try_acquire(_bucket_name, 1)
        path = prefix_slash(path)
        url = _url_base + path
        self.logger.debug("GET url=%s params=%s headers=%s" % (url, params, _headers))
        resp = requests.get(
            url, headers=_headers | {"Shortcut-Token": self.token}, params=params
        )
        self.logger.debug(f"GET response: {resp.status_code} {resp.text}")
        # resp.raise_for_status()
        return resp

    def get_json(self, path: str, params: Mapping[str, str] | None = {}) -> Any:
        """
        Make an HTTP GET call to Shorcut's API and return only the response
        body as a jsonable array or dict.
        """
        return self.get(path, params).json()

    def delete(
        self, path: str, data: Mapping[str, str] | None = {}
    ) -> requests.Response:
        """
        Make an HTTP DELETE call to Shortcut's API.

        Typically used to delete an entity.
        """
        self.limiter.try_acquire(_bucket_name, 1)
        path = prefix_slash(path)
        url = _url_base + path
        self.logger.debug("DELETE url=%s params=%s headers=%s" % (url, data, _headers))
        resp = requests.delete(
            url, headers=_headers | {"Shortcut-Token": self.token}, json=data
        )
        self.logger.debug(f"DELETE response: {resp.status_code} {resp.text}")
        # resp.raise_for_status()
        return resp

    def post(self, path: str, data: Mapping[str, str] | None = {}) -> requests.Response:
        """
        Make an HTTP POST call to Shortcut's API.

        Typically used to create an entity. Other types of requests that
        are either expensive or need consistent parameter serialization
        may also use a POST request.  Serializes params as JSON in the
        request body.
        """
        self.limiter.try_acquire(_bucket_name, 1)
        path = prefix_slash(path)
        url = _url_base + path
        self.logger.debug("POST url=%s params=%s headers=%s" % (url, data, _headers))
        resp = requests.post(
            url, headers=_headers | {"Shortcut-Token": self.token}, json=data
        )
        self.logger.debug(f"POST response: {resp.status_code} {resp.text}")
        # resp.raise_for_status()
        return resp

    def post_json(self, path: str, data: Mapping[str, str] | None = {}) -> Any:
        """
        Make an HTTP POST call to Shortcut's API and return only the response
        body as a jsonable array or dict.
        """
        return self.post(path, data).json()

    def put(self, path: str, data: Mapping[str, str] | None = {}) -> requests.Response:
        """
        Make an HTTP PUT call to Shortcut's API.

        Typically used to update an entity.
        Serializes params as JSON in the request body.
        """
        self.limiter.try_acquire(_bucket_name, 1)
        path = prefix_slash(path)
        url = _url_base + path
        self.logger.debug("PUT url=%s params=%s headers=%s" % (url, data, _headers))
        resp = requests.put(
            url, headers=_headers | {"Shortcut-Token": self.token}, json=data
        )
        self.logger.debug(f"PUT response: {resp.status_code} {resp.text}")
        # resp.raise_for_status()
        return resp

    def put_json(self, path: str, data: Mapping[str, str] | None = {}) -> Any:
        """
        Make an HTTP PUT call to Shortcut's API and return only the response
        body as a jsonable array or dict.
        """
        return self.put(path, data).json()

    def upload_files(self, files: Sequence[str]) -> FileUploads:
        """
        Upload files located at `files` locations.

        The `FileUploads` return type includes a `succeeded` field with a list
        of Shortcut File entities that you can then associate with Shortcut Stories
        by specifying their `file_ids`.
        """
        self.limiter.try_acquire(_bucket_name, 1)
        url = f"{_url_base}/files"
        self.logger.debug(
            "UPLOAD FILES url=%s files=%s headers=%s" % (url, files, _headers)
        )
        file_entities: list[dict[str, Any]] = []
        failed_files: list[str] = []
        responses: list[requests.Response] = []
        headers = dissoc(_headers, "Content-Type") | {
            "Accept": "application/json",
            "Shortcut-Token": self.token,
        }
        for file in files:
            try:
                with open(file, "rb") as f:
                    self.logger.debug(f"File: {f.name} {guess_mime_type(f.name)}")
                    resp = requests.post(
                        url,
                        headers=headers,
                        files=[
                            (
                                "file0",
                                (os.path.basename(f.name), f, guess_mime_type(f.name)),
                            )
                        ],
                    )
                    responses.append(resp)
                    self.logger.debug(
                        f"UPLOAD FILES response: {resp.status_code} {resp.text}"
                    )
                    resp.raise_for_status()
                    resp_json = resp.json()
                    file_entities.append(resp_json[0])
            except Exception as e:
                self.logger.error(f"Failed to upload file {file}", exc_info=e)
                failed_files.append(file)
        return FileUploads(
            responses=responses,
            succeeded=file_entities,
            failed=failed_files,
        )
