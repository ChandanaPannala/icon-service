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
from enum import IntEnum
from typing import Callable

from ..base.address import Address
from .iiss_data_converter import TypeTag, IissDataConverter
from .ipc.proxy import IconProxy


class Message(IntEnum):
    VERSION = 0
    CLAIM = 1
    QUERY = 2
    CALCULATE = 3
    RESULT = 99


class Status(IntEnum):
    SUCCESS = 0
    SYSTEM_FAILURE = 1


class IissProxy(IconProxy):
    def __init__(self):
        super().__init__()
        self._handle_version_func = None
        self._handle_claim_func = None
        self._handle_query_func = None
        self._handle_calculate_func = None

    def set_version_func(self, func: Callable):
        self._handle_version_func = func

    def set_claim_func(self, func: Callable):
        self._handle_claim_func = func

    def set_query_func(self, func: Callable):
        self._handle_query_func = func

    def set_calculate_func(self, func: Callable):
        self._handle_calculate_func = func

    def _receive_data(self, msg: int, data: list):
        if msg == Message.VERSION:
            self._recv_version(data)
        elif msg == Message.CLAIM:
            self._recv_claim(data)
        elif msg == Message.QUERY:
            self._recv_query(data)
        elif msg == Message.CALCULATE:
            self._recv_calculate(data)
        else:
            pass

    def _recv_version(self, data: list):
        version = IissDataConverter.decode(TypeTag.INT, data[0])
        self._handle_version_func(version)

    def _recv_claim(self, data: list):
        address = IissDataConverter.decode(TypeTag.ADDRESS, data[0])
        iscore = IissDataConverter.decode(TypeTag.INT, data[1])
        self._handle_claim_func(address, iscore)

    def _recv_query(self, data: list):
        address = IissDataConverter.decode(TypeTag.ADDRESS, data[0])
        iscore = IissDataConverter.decode(TypeTag.INT, data[1])
        self._handle_calculate_func(address, iscore)

    def _recv_calculate(self, data: list):
        success = IissDataConverter.decode(TypeTag.INT, data[0])
        block_height = IissDataConverter.decode(TypeTag.INT, data[1])
        state_hash = IissDataConverter.decode(TypeTag.BYTES, data[2])
        self._handle_calculate_func(success, block_height, state_hash)

    def send_claim(self, address: 'Address'):
        self._client.send(Message.CLAIM, [IissDataConverter.encode(address)])

    def send_query(self, address: 'Address'):
        self._client.send(Message.QUERY, [IissDataConverter.encode(address)])

    def send_calculate(self, path: str, block_height: int):
        self._client.send(Message.CALCULATE, [IissDataConverter.encode(path), IissDataConverter.encode(block_height)])
