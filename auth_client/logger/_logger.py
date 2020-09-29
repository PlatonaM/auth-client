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

__all__ = ("levels", "init")


from .. import __title__ as TITLE
import logging
import logging.handlers
import typing


msg_fmt = "%(asctime)s - %(levelname)s: [%(name)s] %(message)s"
date_fmt = "%m.%d.%Y %I:%M:%S %p"

logger = logging.getLogger(TITLE)
logger.propagate = False


def init(level: int = logging.INFO, handler: typing.Optional[logging.Handler] = None, formatter: typing.Optional[logging.Formatter] = None) -> None:
    if not handler:
        handler = logging.StreamHandler()
    if not formatter:
        formatter = logging.Formatter(fmt=msg_fmt, datefmt=date_fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def getLogger(name: str) -> logging.Logger:
    return logger.getChild(name)
