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
    def __init__(self, tx_index: int):
        super().__init__()
        # index for IissTxData's key
        self._tx_index = tx_index

    @property
    def tx_index(self):
        return self._tx_index

    def increase_tx_index(self):
        self._tx_index += 1


class IissBatchManager(object):
    def __init__(self, recorded_last_transaction_index: int):
        # last transaction index in current db
        self._recorded_last_transaction_index = recorded_last_transaction_index
        self._iiss_batch_mapper = {}

    def get_batch(self, block_hash: bytes) -> 'IissBatch':
        if block_hash in self._iiss_batch_mapper.keys():
            return self._iiss_batch_mapper[block_hash]
        else:
            return IissBatch(self._recorded_last_transaction_index)

    # todo: rename method
    def update_index_and_clear(self, block_hash) -> None:
        committed_batch: 'IissBatch' = self._iiss_batch_mapper[block_hash]
        self._recorded_last_transaction_index = committed_batch.tx_index
        self._iiss_batch_mapper.clear()
