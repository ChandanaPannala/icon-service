# -*- coding: utf-8 -*-
# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import asyncio
import concurrent.futures
from threading import Lock
from typing import TYPE_CHECKING

from .server import IPCServer

if TYPE_CHECKING:
    from ..base.address import Address
    from asyncio.streams import StreamReader, StreamWriter


class RewardCalcProxy(object):
    """Communicates with Reward Calculator through IPC

    """

    def __init__(self):
        self._msg_id = None
        self._loop = None
        self._queue = None
        self._msgs_to_send = None
        self._server_task = None
        self._lock = Lock()
        self._ipc_server = IPCServer()

    def open(self, path: str):
        self._loop = asyncio.get_running_loop()
        self._queue = asyncio.Queue()
        self._msgs_to_send = {}
        self._msg_id = 0

        self._server_task = self._ipc_server.open(self._loop, self._on_accepted, path)

    def get_msg_id(self):
        msg_id = self._msg_id
        self._msg_id = (msg_id + 1) % 0xffffffff

        return msg_id

    def _on_accepted(self, reader: 'StreamReader', writer: 'StreamWriter'):
        asyncio.create_task(self.on_send(reader, writer))

    async def on_send(self, reader: 'StreamReader', writer: 'StreamWriter'):
        while True:
            work_item = await self._queue.get()
            self._msgs_to_send[work_item[0]] = work_item

    def start(self):
        asyncio.create_task(self._server_task)

    def close(self):
        self._ipc_server = None
        self._lock = None
        self._loop = None

    def calculate(self, iiss_db_path: str, block_height: int):
        """Request RewardCalculator to calculate IScore for every account

        :param iiss_db_path: the absolute path of iiss database
        :param block_height: The blockHeight when this request are sent to RewardCalculator
        """
        pass

    def claim_threadsafe(self, address: 'Address', block_height: int, block_hash: bytes) -> list:
        """Claim IScore of a given address

        :param address: the address to claim
        :param block_height: the height of block which contains this claim tx
        :param block_hash: the hash of block which contains this claim tx
        :return: [i-score(int), block_height(int)]
        """
        pass

    def query_threadsafe(self, address: 'Address') -> list:
        """Returns the I-Score of a given address

        It should be called on not main thread but query thread.

        :param address:
        :return: [i-score(int), block_height(int)]
        """
        future: concurrent.futures.Future = \
            asyncio.run_coroutine_threadsafe(self._query(address), self._loop)
        return future.result()

    async def _query(self, address: 'Address') -> list:
        """

        :param address:
        :return:
        """
        future: asyncio.Future = self._loop.create_future()
        msg_id = self.get_msg_id()
        item = [future, address]

        self._msgs_to_send[msg_id] = item
        self._queue.put_nowait(item)

        await future

        return future.result()

    def commit_block(self, block_height: int, block_hash: bytes) -> list:
        pass

    def rollback_block(self, block_height: int, block_hash: bytes) -> list:
        pass
