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
    from ..iiss_engine import IissGlobalVariable


class StakeDelegator:
    icx_storage: 'IcxStorage' = None
    batch_manager: 'IissBatchManager' = None
    data_storage: 'IissDataStorage' = None
    reward_calc_proxy: 'RewardCalcProxy' = None
    global_variable: 'IissGlobalVariable' = None

    @classmethod
    def handle_set_stake(cls,
                         context: 'IconScoreContext',
                         params: dict,
                         tx_result: 'TransactionResult') -> None:

        address: 'Address' = context.tx.origin
        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_SET_STAKE)
        value: int = ret_params[ConstantKeys.VALUE]

        cls._put_stake_to_state_db(context, address, value)
        # TODO tx_result make

    @classmethod
    def _put_stake_to_state_db(cls,
                               context: 'IconScoreContext',
                               address: 'Address',
                               value: int) -> None:

        if not isinstance(value, int) or value < 0:
            raise InvalidParamsException('Failed to stake: value is not int type or value < 0')

        account: 'Account' = cls.icx_storage.get_account(context, address)
        balance: int = account.balance
        stake: int = account.iiss.stake
        total: int = balance + stake

        if total < value:
            raise InvalidParamsException('Failed to stake: total < stake')

        offset: int = value - stake

        if offset == 0:
            return
        elif offset > 0:
            account.stake(abs(offset))
        else:
            unlock_block_height: int = context.block.height + cls.global_variable.unstake_lock_period
            account.unstake(unlock_block_height, abs(offset))
        cls.icx_storage.put_account(context, account.address, account)

    @classmethod
    def handle_get_stake(cls,
                         context: 'IconScoreContext',
                         params: dict) -> dict:

        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_GET_STAKE)
        address: 'Address' = ret_params[ConstantKeys.ADDRESS]
        return cls._get_stake(context, address)

    @classmethod
    def _get_stake(cls,
                   context: 'IconScoreContext',
                   address: 'Address') -> dict:

        account: 'Account' = cls.icx_storage.get_account(context, address)

        stake: int = 0
        unstake: int = 0
        unstake_block_beight: int = 0
        if account:
            stake: int = account.iiss.stake
            unstake: int = account.iiss.unstake
            unstake_block_beight: int = account.iiss.unstake_block_height

        data = {
            "stake": stake,
            "unstake": unstake,
            "unstakeBlockHeight": unstake_block_beight
        }
        return data
