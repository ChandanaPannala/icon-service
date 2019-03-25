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

from collections import OrderedDict


# todo: Ordered dict is not used
class IissBatch(OrderedDict):
    def __init__(self, db_transaction_index: int):
        super().__init__()
        # index for IissTxData's key
        self._batch_transaction_index = db_transaction_index

    @property
    def batch_transaction_index(self):
        return self._batch_transaction_index

    def increase_transaction_index(self):
        self._batch_transaction_index += 1


class IissBatchManager(object):
    def __init__(self, recorded_last_transaction_index: int):
        # should increase last transaction index (already used index).
        self._db_transaction_index = recorded_last_transaction_index + 1
        self._iiss_batch_mapper = {}

    def get_batch(self, block_hash: bytes) -> 'IissBatch':
        if block_hash in self._iiss_batch_mapper.keys():
            return self._iiss_batch_mapper[block_hash]
        else:
            return IissBatch(self._db_transaction_index)

    # todo: rename method
    def update_index_and_clear_mapper(self, block_hash) -> None:
        self._db_transaction_index = self._iiss_batch_mapper[block_hash].batch_transaction_index

        self._iiss_batch_mapper.clear()

    def update_index_to_zero(self):
        self._db_transaction_index = 0
