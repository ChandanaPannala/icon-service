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

import os
from typing import TYPE_CHECKING

from .database.iiss_db import IissDatabase
from .iiss_msg_data import IissHeader, IissGovernanceVariable, PrepsData, IissTxData, \
    DelegationTx, DelegationInfo, ClaimTx, PRepRegisterTx, PRepUnregisterTx

if TYPE_CHECKING:
    from ..base.address import Address
    from .iiss_msg_data import IissData, IissTx


class IissDataStorage(object):
    _CURRENT_IISS_DB_NAME = "current"
    _PREVIOUS_IISS_DB_NAME = "previous"

    def __init__(self) -> None:
        """Constructor

        :param db: (Database) IISS db wrapper
        """
        # TODO IISS DB 저장클래스 만들기
        self._db = None

    def open(self, path) -> None:
        # todo: path에 대해서 놓친 부분 없는 지 체크하기
        db_path = os.path.join(path, self._CURRENT_IISS_DB_NAME)
        self._db = IissDatabase.from_path(db_path, create_if_missing=True)

    def close(self) -> None:
        """Close the embedded database.
        """
        if self._db:
            self._db = None

    def put(self, batch: dict, iiss_data: 'IissData') -> None:
        # iiss data, batch data에 대한 check logic

        key: bytes = iiss_data.make_key()
        value: bytes = iiss_data.make_value()
        batch.update({key: value})

    def commit(self, batch: dict) -> None:
        # batch data에 대한 check logic

        self._db.write_batch(batch)

        # batch에서 마지막 index를 따로 db에 기록

    def load_last_transaction_index(self) -> int:
        # if there is no data on db, return 0
        tx_sub_db: 'IissDatabase' = self._db.get_sub_db(IissData._prefix)

        last_tx_key, _ = next(tx_sub_db.iterator(reverse=True))
        return int.from_bytes(last_tx_key[2:], "big")

    def create_db_for_calc(self) -> str:
        # todo: db 생성 전에 고려해야할 부분 정리하기
        # db close

        # cp and rename current db

        # clear all data of current db

        # return db path
        pass

    def remove_db_for_calc(self) -> None:
        #
        pass

    # Utils
    @staticmethod
    def create_header(version: int, block_height: int) -> 'IissHeader':
        data = IissHeader()
        data.version: int = version
        data.block_height: int = block_height
        return data

    @staticmethod
    def create_gv_variable(icx_price: int, incentive_rep: int) -> 'IissGovernanceVariable':
        data = IissGovernanceVariable()
        data.icx_price: int = icx_price
        data.incentive_rep: int = incentive_rep
        return data

    @staticmethod
    def create_prep_data(address: 'Address', block_generate_count: int, block_validate_count: int) -> 'PrepsData':
        data = PrepsData()
        data.address: 'Address' = address
        data.block_generate_count: int = block_generate_count
        data.block_validate_count: int = block_validate_count
        return data

    @staticmethod
    def create_tx(address: 'Address', block_height: int, tx_data: 'IissTx') -> 'IissTxData':
        data = IissTxData()
        data.address: 'Address' = address
        data.block_height: int = block_height
        data.data: 'IissTx' = tx_data
        return data

    @staticmethod
    def create_tx_delegation(delegation_infos: list) -> 'DelegationTx':
        tx = DelegationTx()
        tx.delegation_info: list = delegation_infos
        return tx

    @staticmethod
    def create_delegation_info(address: 'Address', value: int) -> 'DelegationInfo':
        info = DelegationInfo()
        info.address: 'Address' = address
        info.value: int = value
        return info

    @staticmethod
    def create_tx_claim() -> 'ClaimTx':
        tx = ClaimTx()
        return tx

    @staticmethod
    def create_tx_prep_reg() -> 'PRepRegisterTx':
        tx = PRepRegisterTx()
        return tx

    @staticmethod
    def create_tx_prep_unreg() -> 'PRepUnregisterTx':
        tx = PRepUnregisterTx()
        return tx
