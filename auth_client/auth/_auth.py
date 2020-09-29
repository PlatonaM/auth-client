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

from .. import http
from ..logger._logger import getLogger
import time
import json
import typing


_logger = getLogger(__name__.split('.', 1)[-1].replace("_", ""))


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
    def __init__(self, url: str, usr: str, pw: str, id: str, timeout: typing.Optional[int] = 15):
        """
        Create a client object.
        :param url: URL of token provider.
        :param usr: Username.
        :param pw: Password.
        :param id: Client ID required by the token provider.
        :param timeout: Request timeout.
        """
        self.__url = url
        self.__usr = usr
        self.__pw = pw
        self.__id = id
        self.__timeout = timeout
        self.__access_token = None
        self.__refresh_token = None
        self.__token_type = None
        self.__not_before_policy = None
        self.__session_state = None

    def getAccessToken(self) -> str:
        """
        Retrieves new access token or refreshes existing access token. Returns access token.
        :return: Access token as string.
        """
        try:
            if self.__access_token:
                if int(time.time()) - self.__access_token.time_stamp >= self.__access_token.max_age:
                    _logger.debug('access token expired')
                    if int(time.time()) - self.__refresh_token.time_stamp >= self.__refresh_token.max_age:
                        _logger.debug('refresh token expired')
                        self.__tokenRequest()
                    else:
                        self.__refreshRequest()
            else:
                self.__tokenRequest()
            return self.__access_token.token
        except (RequestError, ResponseError) as ex:
            raise NoTokenError(ex)

    def getHeader(self) -> dict:
        """
        Convenience method wrapping getAccessToken. Returns authorization HTTP header with access token.
        :return: Authorization HTTP header.
        """
        return {"Authorization": "Bearer {}".format(self.getAccessToken())}

    def __setResponse(self, payload: str) -> None:
        try:
            payload = json.loads(payload)
            self.__access_token = Token(payload['access_token'], payload['expires_in'])
            self.__refresh_token = Token(payload['refresh_token'], payload['refresh_expires_in'])
            self.__token_type = payload['token_type']
            self.__not_before_policy = payload['not-before-policy']
            self.__session_state = payload['session_state']
        except (json.JSONDecodeError, TypeError) as ex:
            _logger.error("could not decode response - {}".format(ex))
            raise ResponseError
        except KeyError as ex:
            _logger.error("malformed response - missing key {}".format(ex))
            raise ResponseError

    def __request(self, r_type: str, payload: dict) -> None:
        req = http.Request(
            url=self.__url,
            method=http.Method.POST,
            body=payload,
            content_type=http.ContentType.form,
            timeout=self.__timeout
        )
        try:
            resp = req.send()
            if resp.status == 200:
                self.__setResponse(resp.body)
            else:
                _logger.error('{} request got bad response - {}'.format(r_type, resp))
                raise RequestError
        except (http.SocketTimeout, http.URLError) as ex:
            _logger.error('{} request failed - {}'.format(r_type, ex))
            raise RequestError

    def __tokenRequest(self) -> None:
        _logger.debug("requesting new access token ...")
        payload = {
            'grant_type': 'password',
            'username': self.__usr,
            'password': self.__pw,
            'client_id': self.__id
        }
        self.__request('token', payload)
        _logger.debug("requesting new access token successful")

    def __refreshRequest(self) -> None:
        _logger.debug("requesting access token refresh ...")
        payload = {
            'grant_type': 'refresh_token',
            'client_id': self.__id,
            'refresh_token': self.__refresh_token.token
        }
        self.__request('refresh', payload)
        _logger.debug("requesting access token refresh successful")
