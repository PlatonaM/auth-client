"""
   Copyright 2020 InfAI (CC SES)

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

__all__ = ("Method", "ContentType", "Request", "URLError", "SocketTimeout")


from .._logger._logger import get_logger
from ._response import Response
import typing
import socket
import urllib.error
import urllib.request
import urllib.parse
import json


_logger = get_logger(__name__.rsplit(".", 1)[-1].replace("_", ""))


class SocketTimeout(Exception):
    pass


class URLError(Exception):
    pass


ca_file = None

try:
    import certifi
    ca_file = certifi.where()
except ImportError as ex:
    pass


class Method:
    HEAD = "HEAD"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    OPTIONS = "OPTIONS"


class ContentType:
    json = "application/json"
    form = "application/x-www-form-urlencoded"
    plain = "text/plain"


class Request:
    def __init__(self, url: str, method: str = Method.GET, body: typing.Optional[typing.Union[typing.Iterable, typing.SupportsAbs]] = None, content_type: typing.Optional[str] = None, headers: typing.Optional[dict] = None, timeout: int = 30):
        self.__url = url
        self.__method = method
        self.__body = body
        self.__headers = headers or dict()
        self.__timeout = timeout
        self.__request = None
        if self.__body and not content_type:
            raise RuntimeError("missing content type for body")
        if self.__body and content_type:
            if content_type == ContentType.json:
                self.__body = json.dumps(self.__body).encode()
            elif content_type == ContentType.form:
                self.__body = urllib.parse.urlencode(self.__body).encode()
            elif content_type == ContentType.plain:
                if type(self.__body) not in (int, float, complex, str):
                    _logger.warning("body with none primitive type '{}' will be converted to string representation".format(type(body).__name__))
                self.__body = str(self.__body).encode()
            else:
                raise RuntimeError("unsupported content type '{}'".format(content_type))
            self.__headers["content-type"] = content_type
        self.__request = urllib.request.Request(
            self.__url,
            data=self.__body,
            headers=self.__headers,
            method=self.__method
        )

    def send(self) -> Response:
        try:
            resp = urllib.request.urlopen(
                self.__request,
                timeout=self.__timeout,
                cafile=ca_file,
                context=None
            )
            return Response(
                status=resp.getcode(),
                body=resp.read().decode(),
                headers=dict(resp.info().items())
            )
        except urllib.error.HTTPError as ex:
            return Response(
                status=ex.code,
                body=ex.reason,
                headers=dict(ex.headers.items())
            )
        except urllib.error.URLError as ex:
            _logger.error("{} - '{}'".format(ex, self.__url))
            raise URLError(ex)
        except socket.timeout as ex:
            _logger.error("timed out - '{}' - {}".format(self.__url, self.__method))
            raise SocketTimeout(ex)
