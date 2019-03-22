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

from typing import TYPE_CHECKING

from ...base.exception import InvalidParamsException
from ...base.type_converter_templates import ParamType, ConstantKeys
from ...base.type_converter import TypeConverter

from ..database.iiss_batch import IissBatchManager
from ..iiss_data_storage import IissDataStorage
from ..reward_calc_proxy import RewardCalcProxy

if TYPE_CHECKING:
    from ...iconscore.icon_score_result import TransactionResult
    from ...iconscore.icon_score_context import IconScoreContext
    from ...icx.icx_storage import IcxStorage
    from ...icx.icx_account import Account
    from ...base.address import Address
    from ..database.iiss_batch import IissBatch
    from ..iiss_engine import IissGlobalVariable
    from ..iiss_msg_data import ClaimTx, IissTxData


class ClaimDelegator:
    icx_storage: 'IcxStorage' = None
    batch_manager: 'IissBatchManager' = None
    data_storage: 'IissDataStorage' = None
    reward_calc_proxy: 'RewardCalcProxy' = None
    global_variable: 'IissGlobalVariable' = None

    @classmethod
    def handle_claim_i_score(cls,
                             context: 'IconScoreContext',
                             params: dict,
                             tx_result: 'TransactionResult') -> None:
        address: 'Address' = context.tx.origin
        # ret_params: dict = TypeConverter.convert(params, ParamType.IISS_CLAIM_I_SCORE)

        cls._put_claim_score_to_state_db(context, address)
        batch: 'IissBatch' = cls.batch_manager.get_batch(context.block.hash)
        cls._put_claim_score_to_iiss_db(batch, address, context.block.height)
        # TODO tx_result make

    @classmethod
    def _put_claim_score_to_state_db(cls,
                                     context: 'IconScoreContext',
                                     address: 'Address') -> None:
        # TODO invoke to RC
        cls.reward_calc_proxy.claim(address, context.block.height, context.block.hash)

    @classmethod
    def _put_claim_score_to_iiss_db(cls,
                                    batch: 'IissBatch',
                                    address: 'Address',
                                    block_height: int) -> None:
        claim_tx: 'ClaimTx' = cls.data_storage.create_tx_claim()
        iiss_tx_data: 'IissTxData' = cls.data_storage.create_tx(address, block_height, claim_tx)
        cls.data_storage.put(batch, iiss_tx_data)

    @classmethod
    def handle_query_i_score(cls,
                             context: 'IconScoreContext',
                             params: dict) -> dict:
        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_QUERY_I_SCORE)
        address: 'Address' = ret_params[ConstantKeys.ADDRESS]
        return cls._get_i_score_from_rc(address)

    @classmethod
    def _get_i_score_from_rc(cls, address: 'Address') -> dict:

        # TODO query from RC
        address: 'Address' = None
        iscore: int = 1000 * 10 ** 18
        icx: int = iscore // 10 ** 3
        block_height: int = 100

        data = [address, iscore, icx, block_height]

        address: 'Address' = data[0]
        iscore: int = data[1]
        icx: int = iscore // 10 ** 3
        block_height: int = data[2]

        data = {
            "iscore": iscore,
            "icx": icx,
            "blockHeight": block_height
        }

        return data
