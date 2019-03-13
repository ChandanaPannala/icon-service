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

if TYPE_CHECKING:
    from ..iconscore.icon_score_context import IconScoreContext


class IissEngine:

    def __init__(self):
        # self._iiss_data_db = None # iiss_data_level_db_instance (#쿼리 불가)
        # self._context_data_db = None # iiss용 상태db저장용, 만약 이렇게 가는거면 기존 state와 독립적으로 가야함. ex)account
        # self._perp_list: list = [] # 후보자 관리
        # self._socket_engine = None # IPC 통신을 하기위한 엔
        pass

    def open(self):
        # self._init_prep_order_list() # -> 비동기? 동기? LC에서 기다리고 IISSEngine이 다 끝나면 Hello를 다시 보내줄 것인가?
        # self._connect_iiss_data_db()
        pass

    def close(self):
        pass

    def invoke(self, context: 'IconScoreContext',
               data_type: str,
               data: dict) -> None:
        # self._call(context, data_type, data)
        pass

    def query(self, context: IconScoreContext,
              data_type: str,
              data: dict) -> Any:
        # ret = self._call(context, data_type, data)
        return None

    def commit(self):
        # self._iiss_data_db.write_batch()
        pass

    def rollback(self):
        # self._iiss_data_db.clear()
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
    # def _call(self,
    #           context: 'IconScoreContext',
    #           method: str,
    #           params: dict) -> Any:
    #     """Call invoke and query requests in jsonrpc format"""
    #     # invoke, query에서 method별로 이곳에서 각각 실행
    #     pass
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
