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

from typing import TYPE_CHECKING, Any

from ..base.exception import InvalidParamsException
from ..base.type_converter import TypeConverter
from ..base.type_converter_templates import ParamType, ConstantKeys

from ..iiss.iiss_data_storage import IissDataStorage

if TYPE_CHECKING:
    from ..iconscore.icon_score_result import TransactionResult
    from ..iconscore.icon_score_context import IconScoreContext
    from ..base.address import Address
    from ..icx.icx_storage import IcxStorage
    from ..icx.icx_account import Account, DelegationInfo
    from .iiss_msg_data import IissTxData, StakeTx, DelegationInfo, DelegationTx


class IissEngine:
    icx_storage: 'IcxStorage' = None

    def __init__(self):
        self._invoke_handlers: dict = {
            'setStake': self._handle_set_stake,
            'setDelegation': self._handle_set_delegation
        }

        self._query_handler: dict = {
            'getStake': self._handle_get_stake,
            'getDelegation': self._handle_get_delegation
        }

        self._iiss_data_storage: 'IissDataStorage' = None

        # iiss데이터db가 글로벌 정보는 임시로 저장
        # self._iiss_data_db = None # iiss_data_level_db_instance
        # self._context_data_db = None # iiss용 상태db저장용, 만약 이렇게 가는거면 기존 state와 독립적으로 가야함. ex)account
        # self._perp_list: list = [] # 후보자 관리
        # self._socket_engine = None # IPC 통신을 하기위한 엔
        pass

    def open(self):
        self._iiss_data_storage: 'IissDataStorage' = IissDataStorage()
        self._iiss_data_storage.open()

        # self._init_prep_order_list() # -> 비동기? 동기? LC에서 기다리고 IISSEngine이 다 끝나면 Hello를 다시 보내줄 것인가?
        # self._connect_iiss_data_db()
        pass

    def close(self):
        self._iiss_data_storage.close()

    def invoke(self, context: 'IconScoreContext',
               data: dict,
               tx_result: 'TransactionResult') -> None:
        method: str = data['method']
        params: dict = data['params']

        handler: callable = self._invoke_handlers[method]
        handler(context, params, tx_result)

    def query(self, context: 'IconScoreContext',
              data: dict) -> Any:
        method: str = data['method']
        params: dict = data['params']

        handler: callable = self._query_handler[method]
        ret = handler(context, params)
        return ret

    def _handle_set_stake(self,
                          context: 'IconScoreContext',
                          params: dict,
                          tx_result: 'TransactionResult') -> None:
        address: 'Address' = context.tx.origin
        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_SET_STAKE)
        value: int = ret_params[ConstantKeys.VALUE]

        self._put_stake_to_state_db(context, address, value)
        self._put_stake_to_iiss_db(address, context.block.height, value)
        # TODO tx_result make

    def _put_stake_to_state_db(self,
                               context: 'IconScoreContext',
                               address: 'Address',
                               value: int) -> None:

        if not isinstance(value, int) or value < 0:
            raise InvalidParamsException('Failed to stake: value is not int type or value < 0')

        account: 'Account' = self.icx_storage.get_account(context, address)
        balance: int = account.balance
        stake: int = account.iiss.stake
        total: int = balance + stake

        if total < value:
            raise InvalidParamsException('Failed to stake: total < stake')

        offset: int = value - stake
        if offset > 0:
            account.stake(abs(offset))
        elif offset < 0:
            account.unstake(abs(offset))
        else:
            return
        self.icx_storage.put_account(context, account.address, account)

    def _put_stake_to_iiss_db(self,
                              address: 'Address',
                              block_height: int,
                              value: int) -> None:

        stake_tx: 'StakeTx' = self._iiss_data_storage.create_tx_stake(value)
        iiss_data: 'IissTxData' = self._iiss_data_storage.create_tx(address, block_height, stake_tx)
        self._iiss_data_storage.put(iiss_data)

    def _handle_get_stake(self,
                          context: 'IconScoreContext',
                          params: dict) -> int:

        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_GET_STAKE)
        address: 'Address' = ret_params[ConstantKeys.ADDRESS]
        return self._get_stake(context, address)

    def _get_stake(self,
                   context: 'IconScoreContext',
                   address: 'Address') -> int:
        account: 'Account' = self.icx_storage.get_account(context, address)

        stake: int = 0
        if account:
            stake: int = account.iiss.stake
        return stake

    def _handle_set_delegation(self,
                               context: 'IconScoreContext',
                               params: dict,
                               tx_result: 'TransactionResult') -> None:

        address: 'Address' = context.tx.origin
        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_SET_STAKE)
        data: list = ret_params[ConstantKeys.DELEGATIONS]

        self._put_delegation_to_state_db(context, address, data)
        self._put_delegation_to_iiss_db(address, context.block.height, data)
        # TODO tx_result make

    def _put_delegation_to_state_db(self,
                                    context: 'IconScoreContext',
                                    from_address: 'Address',
                                    delegations: list) -> bool:

        if not isinstance(delegations, list):
            raise InvalidParamsException('Failed to delegation: delegations is not list type')

        from_account: 'Account' = self.icx_storage.get_account(context, from_address)
        stake: int = from_account.iiss.stake

        total_amoount: int = 0
        update_list: list = []
        for address, value in delegations:
            target_account: 'Account' = self.icx_storage.get_account(context, address)
            if from_account.delegation(target_account, value):
                update_list.append(target_account)
            total_amoount += value

        if stake < total_amoount:
            raise InvalidParamsException('Failed to delegation: stake < total_delegations')

        self.icx_storage.put_account(context, from_account.address, from_account)
        for account in update_list:
            self.icx_storage.put_account(context, account.address, account)
        return True

    def _put_delegation_to_iiss_db(self,
                                   address: 'Address',
                                   block_height: int,
                                   delegations: list) -> bool:

        delegation_list: list = []

        for address, value in delegations:
            info: 'DelegationInfo' = self._iiss_data_storage.create_delegation_info(address, value)
            delegation_list.append(info)

        delegation_tx: 'DelegationTx' = self._iiss_data_storage.create_tx_delegation(delegation_list)
        self._iiss_data_storage.create_tx(address, block_height, delegation_tx)
        return True

    def _handle_get_delegation(self,
                               context: 'IconScoreContext',
                               params: dict) -> dict:

        ret_params: dict = TypeConverter.convert(params, ParamType.IISS_GET_STAKE)
        address: 'Address' = ret_params[ConstantKeys.ADDRESS]
        return self._get_delegation(context, address)

    def _get_delegation(self,
                        context: 'IconScoreContext',
                        address: 'Address') -> dict:
        account: 'Account' = self.icx_storage.get_account(context, address)
        return {}

    def commit(self):
        self._iiss_data_storage.commit()

    def rollback(self):
        # self._iiss_data_storage.commit()
        pass

    # def _init_prep_order_list(self):
    #     # 상태 db에서 기록된 prep후보자 리스트를 전수조사하여 메모리상에 리스트를 생성
    #     pass
    #
    # def _update_prep_order_list(self):
    #     # 소팅하여 리스트 갱신
    #     pass
    #
    # def _init_reward_calculate(self):
    #     # IPC 통신을 하기위한 초기설정
    #     pass
    #
    #
    # def _set_global_value_into_state_DB(self):
    #     # IISS에 필요한 DB데이터를 기록한다.
    #     # 예로 db_path, tx_index
    #     pass
    #
    # def _get_global_value_from_state_DB(self):
    #     # IISS_DB 쓰는데 필요한 데이터를 상태 DB에서 읽는다.
    #     pass
    #
    # def _make_next_iiss_data_db_path(self):
    #     # 다음 iiss data path생성
    #     pass
    #
    # def _create_iiss_data_db(self):
    #     # 새로운 IISS Data DB생성
    #     pass
    #
    # def _connect_iiss_data_db(self):
    #     # 기존의 IISS Data DB연결
    #     # DB를 생성하지 않는다.
    #     pass
    #
    # # issurance? 발행
    # def _issurance(self):
    #     pass
    #
    # # invoke IISS tx
    # def _handle_invoke_iiss(self):
    #     pass
    #
    # def _make_tx_result_for_iiss(self):
    #     # IISS에 맞는 txresult를 만든다.
    #     pass
    #
    # # invoke state DB and IPC
    # def _invoke_tx_stake(self):
    #     pass
    #
    # def _invoke_tx_delegate(self):
    #     pass
    #
    # def _invoke_tx_claim(self):
    #     pass
    #
    # def _invoke_tx_reg_prep(self):
    #     pass
    #
    # def _invoke_tx_un_reg_prep(self):
    #     pass
    #
    # def _invoke_tx_set_reg_prep(self):
    #     pass
    #
    # # query
    # def _query_get_stake(self):
    #     pass
    #
    # def _get_delegation(self):
    #     pass
    #
    # def _query_i_score(self):
    #     pass
    #
    # def _query_get_perp_candidate(self):
    #     pass
    #
    # def _query_get_perp_candidate_stat(self):
    #     pass
    #
    # def _query_get_prep_candidate_delegation_info(self):
    #     pass
    #
    # def _query_get_prep_list(self):
    #     pass
    #
    # def _query_get_prep_candidate_list(self):
    #     pass
    #
    # # DB
    # # put StateDB for IISS
    # def _put_prep_data_state_db(self):
    #     pass
    #
    # def _put_stake_into_state_db(self):
    #     pass
    #
    # def _put_delegate_into_state_db(self):
    #     pass
    #
    # # get StateDB for IISS
    # def _get_prep_data_from_state_db(self):
    #     pass
    #
    # def _get_stake_from_state_db(self):
    #     pass
    #
    # def _get_delegate_from_state_db(self):
    #     pass
    #
    # # make IISS Data (iiss_data_storage에서 한다?)
    # def _handle_tx_convert_iiss_data(self):
    #     pass
    #
    # def _put_iiss_header_into_iiss_data(self):
    #     pass
    #
    # def _put_iiss_governance_variable_into_iiss_data(self):
    #     pass
    #
    # def _put_iiss_perp_data_into_iiss_data(self):
    #     pass
    #
    # def _put_iiss_tx_data_into_iiss_data(self):
    #     pass
