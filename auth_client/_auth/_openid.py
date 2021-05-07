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

__all__ = ("Client", "NoTokenError")


from .. import _http
from .._logger._logger import get_logger
import time
import json
import typing


_logger = get_logger(__name__.rsplit(".", 1)[-1].replace("_", ""))


class AuthError(Exception):
    pass


class RequestError(AuthError):
    pass


class ResponseError(AuthError):
    pass


class NoTokenError(AuthError):
    pass


class Token:
    def __init__(self, token: str, max_age: int):
        self.token = token
        self.max_age = max_age
        self.time_stamp = int(time.time())


class Client:
    def __init__(self, url: str, client_id: str, secret: typing.Optional[str] = None, user: typing.Optional[str] = None, password: typing.Optional[str] = None, user_id: typing.Optional[str] = None, timeout: typing.Optional[int] = 15):
        """
        Create a client object.
        :param url: URL of authorization endpoint.
        :param client_id: Client ID required by the authorization endpoint.
        :param secret: Secret, required by the client-credentials and token-exchange grant type.
        :param user: Username, required by the resource-owner-password grant type.
        :param password: Password, required by the resource-owner-password grant type.
        :param user_id: User ID, required by the token-exchange grant type.
        :param timeout: Token request timeout.
        """
        self.__url = url
        self.__usr = user
        self.__pw = password
        self.__id = client_id
        self.__secret = secret
        self.__usr_id = user_id
        self.__timeout = timeout
        self.__access_token = None
        self.__refresh_token = None
        self.__token_type = None
        self.__not_before_policy = None
        self.__session_state = None

    def get_access_token(self) -> str:
        """
        Retrieves new access token or refreshes existing access token. Returns access token.
        :return: Access token as string.
        """
        try:
            if self.__access_token:
                if int(time.time()) - self.__access_token.time_stamp >= self.__access_token.max_age:
                    _logger.debug("access token expired")
                    if int(time.time()) - self.__refresh_token.time_stamp >= self.__refresh_token.max_age:
                        _logger.debug("refresh token expired")
                        self.__token_request()
                    else:
                        self.__refresh_request()
            else:
                self.__token_request()
            return self.__access_token.token
        except (RequestError, ResponseError) as ex:
            raise NoTokenError(ex)

    def get_header(self) -> dict:
        """
        Convenience method wrapping getAccessToken. Returns authorization HTTP header with access token.
        :return: Authorization HTTP header.
        """
        return {"Authorization": "Bearer {}".format(self.get_access_token())}

    def __set_response(self, payload: str) -> None:
        try:
            payload = json.loads(payload)
            self.__access_token = Token(payload["access_token"], payload["expires_in"])
            self.__refresh_token = Token(payload["refresh_token"], payload["refresh_expires_in"])
            self.__token_type = payload["token_type"]
            self.__not_before_policy = payload["not-before-policy"]
            self.__session_state = payload["session_state"]
        except (json.JSONDecodeError, TypeError) as ex:
            _logger.error("could not decode response - {}".format(ex))
            raise ResponseError
        except KeyError as ex:
            _logger.error("malformed response - missing key {}".format(ex))
            raise ResponseError

    def __request(self, r_type: str, payload: dict) -> None:
        req = _http.Request(
            url=self.__url,
            method=_http.Method.POST,
            body=payload,
            content_type=_http.ContentType.form,
            timeout=self.__timeout
        )
        try:
            resp = req.send()
            if resp.status == 200:
                self.__set_response(resp.body)
            else:
                _logger.error("{} request got bad response - {}".format(r_type, resp.status))
                raise RequestError
        except (_http.SocketTimeout, _http.URLError) as ex:
            _logger.error("{} request failed - {}".format(r_type, ex))
            raise RequestError

    def __token_request(self) -> None:
        _logger.debug("requesting new access token ...")
        payload = {"client_id": self.__id}
        if self.__usr_id and self.__secret:
            _logger.debug("using token-exchange grant type")
            payload["grant_type"] = "urn:ietf:params:oauth:grant-type:token-exchange"
            payload["client_secret"] = self.__secret
            payload["requested_subject"] = self.__usr_id
        elif self.__secret:
            _logger.debug("using client-credentials grant type")
            payload["grant_type"] = "client_credentials"
            payload["client_secret"] = self.__secret
        elif self.__usr and self.__pw:
            _logger.debug("using resource-owner-password grant type")
            payload["grant_type"] = "password"
            payload["username"] = self.__usr
            payload["password"] = self.__pw
        else:
            _logger.error("missing credentials for supported grant types")
            raise RequestError
        self.__request("token", payload)
        _logger.debug("requesting new access token successful")

    def __refresh_request(self) -> None:
        _logger.debug("requesting access token refresh ...")
        payload = {
            "grant_type": "refresh_token",
            "client_id": self.__id,
            "refresh_token": self.__refresh_token.token
        }
        if self.__secret:
            payload["client_secret"] = self.__secret
        self.__request("refresh", payload)
        _logger.debug("requesting access token refresh successful")
