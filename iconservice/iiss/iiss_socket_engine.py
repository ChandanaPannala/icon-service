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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .iiss_proxy import IissProxy
    from ..base.address import Address


class IissSocketEngine(object):
    def __init__(self, proxy: 'IissProxy'):
        self._proxy = proxy
        self._proxy.set_version_func(self._handle_version)
        self._proxy.set_claim_func(self._handle_claim)
        self._proxy.set_query_func(self._handle_query)
        self._proxy.set_calculate_func(self._handle_calculate)

    # main server
    def connect(self, addr: str):
        self._proxy.connect(addr)

    def process(self):
        self._proxy.loop()

    def send_claim(self, address: 'Address'):
        self._proxy.send_claim(address)

    def send_query(self, address: 'Address'):
        self._proxy.send_query(address)

    def send_calculate(self, path: str, block_height: int):
        self._proxy.send_calculate(path, block_height)

    def _handle_version(self, version: int):
        pass

    def _handle_claim(self, address: 'Address', i_score: int):
        pass

    def _handle_query(self, address: 'Address', i_score: int):
        pass

    def _handle_calculate(self, success: bool, block_height: int, state_hash: bytes):
        pass
