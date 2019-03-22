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

from ...icon_constant import IISS_MAX_DELEGATION_LIST
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
    from ...icx.icx_account import Account, DelegationInfo
    from ...base.address import Address
    from ..database.iiss_batch import IissBatch
    from ..iiss_engine import IissGlobalVariable
    from ..iiss_msg_data import DelegationTx, IissTxData


class DelegationDelegator:
    icx_storage: 'IcxStorage' = None
    batch_manager: 'IissBatchManager' = None
    data_storage: 'IissDataStorage' = None
    reward_calc_proxy: 'RewardCalcProxy' = None
    global_variable: 'IissGlobalVariable' = None

    @classmethod
    def handle_set_delegation(cls,
                               context: 'IconScoreContext',
                               params: dict,
                               tx_result: 'TransactionResult') -> None:

        address: 'Address' = context.tx.origin
        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_SET_STAKE)
        data: list = ret_params[ConstantKeys.DELEGATIONS]

        cls._put_delegation_to_state_db(context, address, data)
        batch: 'IissBatch' = cls.batch_manager.get_batch(context.block.hash)
        cls._put_delegation_to_iiss_db(batch, address, context.block.height, data)
        # TODO tx_result make

    @classmethod
    def _put_delegation_to_state_db(cls,
                                    context: 'IconScoreContext',
                                    from_address: 'Address',
                                    delegations: list) -> None:

        if not isinstance(delegations, list):
            raise InvalidParamsException('Failed to delegation: delegations is not list type')

        if len(delegations) >= IISS_MAX_DELEGATION_LIST:
            raise InvalidParamsException(f'Failed to delegation: Overflow Max Input List')

        from_account: 'Account' = cls.icx_storage.get_account(context, from_address)
        stake: int = from_account.iiss.stake

        total_amoount: int = 0
        update_list: dict = {}

        for address in from_account.iiss.delegations:
            target_account: 'Account' = cls.icx_storage.get_account(context, address)
            if from_account.delegation(target_account, 0):
                update_list[address] = target_account

        for address, value in delegations:
            target_account: 'Account' = cls.icx_storage.get_account(context, address)
            if from_account.delegation(target_account, value):
                update_list[address] = target_account
            total_amoount += value

        if len(from_account.iiss.delegations) >= IISS_MAX_DELEGATION_LIST:
            raise InvalidParamsException(f'Failed to delegation: Overflow Max Account List')

        if stake < total_amoount:
            raise InvalidParamsException('Failed to delegation: stake < total_delegations')

        cls.icx_storage.put_account(context, from_account.address, from_account)
        for account in update_list:
            cls.icx_storage.put_account(context, account.address, account)

    @classmethod
    def _put_delegation_to_iiss_db(cls,
                                   batch: "IissBatch",
                                   address: 'Address',
                                   block_height: int,
                                   delegations: list) -> None:

        delegation_list: list = []

        for address, value in delegations:
            info: 'DelegationInfo' = cls.data_storage.create_delegation_info(address, value)
            delegation_list.append(info)

        delegation_tx: 'DelegationTx' = cls.data_storage.create_tx_delegation(delegation_list)
        iiss_tx_data: 'IissTxData' = cls.data_storage.create_tx(address, block_height, delegation_tx)
        cls.data_storage.put(batch, iiss_tx_data)

    @classmethod
    def handle_get_delegation(cls,
                               context: 'IconScoreContext',
                               params: dict) -> dict:

        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_GET_STAKE)
        address: 'Address' = ret_params[ConstantKeys.ADDRESS]
        return cls._get_delegation(context, address)

    @classmethod
    def _get_delegation(cls,
                        context: 'IconScoreContext',
                        address: 'Address') -> dict:

        account: 'Account' = cls.icx_storage.get_account(context, address)

        total_delegated: int = 0
        delegation_list: list = []
        for key, info in account.iiss.delegations.items():
            delegation_list.append(info.to_dict())
            total_delegated += info.value

        data = {
            "delegations": delegation_list,
            "totalDelegated": total_delegated
        }

        return data
