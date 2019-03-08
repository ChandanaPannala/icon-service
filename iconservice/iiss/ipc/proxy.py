# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Any, Tuple
from abc import ABCMeta, abstractmethod
from ..ipc.client import Client


class Codec(metaclass=ABCMeta):
    @abstractmethod
    def encode(self, o: Any) -> Tuple[int, bytes]:
        pass

    @abstractmethod
    def decode(self, t: int, bs: bytes) -> Any:
        pass


class IconProxy:
    def __init__(self):
        self._client = Client()

    def connect(self, addr):
        self._client.connect(addr)

    # 레이어를 하나 더 만들어 둔다.
    # async 방식으로 개선 msgid가 필요할수도..
    def loop(self):
        while True:
            msg, data = self._client.receive()
            self._receive_data(msg, data)

    @abstractmethod
    def _receive_data(self, msg: int, data: list):
        pass
