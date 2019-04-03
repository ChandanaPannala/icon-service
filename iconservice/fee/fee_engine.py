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

import typing
from enum import IntEnum
from typing import List, Dict, Optional

from .deposit import Deposit
from .fee_storage import Fee, FeeStorage
from ..base.address import ZERO_SCORE_ADDRESS
from ..base.exception import InvalidRequestException, InvalidParamsException
from ..base.type_converter import TypeConverter
from ..base.type_converter_templates import ParamType
from ..iconscore.icon_score_event_log import EventLogEmitter
from ..icx.icx_engine import IcxEngine
from ..utils import to_camel_case

if typing.TYPE_CHECKING:
    from ..base.address import Address
    from ..deploy.icon_score_deploy_storage import IconScoreDeployInfo
    from ..deploy.icon_score_deploy_storage import IconScoreDeployStorage
    from ..iconscore.icon_score_context import IconScoreContext
    from ..icx.icx_storage import IcxStorage


class ScoreFeeInfo:
    """
    Fee information of a SCORE
    """

    def __init__(self, score_address: 'Address'):
        # SCORE address
        self.score_address: 'Address' = score_address
        # List of deposits
        self.deposits: List[Deposit] = []
        # fee sharing ratio that SCORE pays
        self.sharing_ratio: int = 0
        # available virtual STEPs to use
        self.available_virtual_step: int = 0
        # available deposits to use
        self.available_deposit: int = 0

    def to_dict(self, casing: Optional = None) -> dict:
        """
        Returns properties as `dict`
        :return: a dict
        """
        new_dict = {}
        for key, value in self.__dict__.items():
            if value is None:
                # Excludes properties which have `None` value
                continue

            new_dict[casing(key) if casing else key] = value

        return new_dict


class FeeEngine:
    """
    Presenter of the fee operation.

    [Role]
    - State DB CRUD
    - Business logic (inc. Calculation)
    """

    _MAX_DEPOSIT_AMOUNT = 100_000 * 10 ** 18

    _MIN_DEPOSIT_AMOUNT = 5_000 * 10 ** 18

    _MAX_DEPOSIT_PERIOD = 31_104_000

    _MIN_DEPOSIT_PERIOD = 1_296_000

    def __init__(self,
                 deploy_storage: 'IconScoreDeployStorage',
                 fee_storage: 'FeeStorage',
                 icx_storage: 'IcxStorage',
                 icx_engine: 'IcxEngine'):

        self._deploy_storage = deploy_storage
        self._fee_storage = fee_storage
        self._icx_storage = icx_storage
        self._icx_engine = icx_engine

    def set_fee_sharing_ratio(self,
                              context: 'IconScoreContext',
                              sender: 'Address',
                              score_address: 'Address',
                              ratio: int) -> None:
        """
        Sets the fee sharing ratio that SCORE pays.

        :param context: IconScoreContext
        :param sender: msg sender address
        :param score_address: SCORE address
        :param ratio: sharing ratio in percent (0-100)
        """

        self._check_score_ownership(context, sender, score_address)

        if not (0 <= ratio <= 100):
            raise InvalidRequestException('Invalid ratio')

        score_fee_info = self._get_or_create_score_fee(context, score_address)
        score_fee_info.ratio = ratio

        self._fee_storage.put_score_fee(context, score_address, score_fee_info)

        # return ratio

    def get_fee_sharing_ratio(self,
                              context: 'IconScoreContext',
                              score_address: 'Address') -> int:
        """
        Gets the fee sharing ratio from score info

        :param context: IconScoreContext
        :param score_address: SCORE address
        :return: sharing ratio in percent (0-100)
        """

        self._check_score_valid(context, score_address)

        score_fee_info = self._fee_storage.get_score_fee(context, score_address)
        return score_fee_info.ratio if score_fee_info is not None else 0

    def get_score_fee_info(self,
                           context: 'IconScoreContext',
                           score_address: 'Address',
                           block_number: int) -> ScoreFeeInfo:
        """
        Gets the SCORE information

        :param context: IconScoreContext
        :param score_address: SCORE address
        :param block_number: current block number
        :return: score information in dict
                - SCORE Address
                - Amount of issued total virtual step
                - Amount of Used total virtual step
                - contracts in list
        """

        self._check_score_valid(context, score_address)

        score_fee_info_from_storage = self._get_or_create_score_fee(context, score_address)

        score_fee_info = ScoreFeeInfo(score_address)
        score_fee_info.sharing_ratio = score_fee_info_from_storage.ratio

        # Appends all deposits
        for deposit in self._deposit_generator(context, score_fee_info_from_storage.head_id):
            score_fee_info.deposits.append(deposit)

            # Retrieves available virtual STEPs and deposits
            if block_number < deposit.expires:
                score_fee_info.available_virtual_step += deposit.available_virtual_step
                score_fee_info.available_deposit += deposit.available_deposit

        return score_fee_info

    def deposit_fee(self,
                    context: 'IconScoreContext',
                    tx_hash: bytes,
                    sender: 'Address',
                    score_address: 'Address',
                    amount: int,
                    block_number: int,
                    period: int) -> None:
        """
        Deposits ICXs for the SCORE.
        It may be issued the virtual STEPs for the SCORE to be able to pay share fees.

        :param context: IconScoreContext
        :param tx_hash: tx hash of the deposit transaction
        :param sender: ICX sender
        :param score_address: SCORE
        :param amount: amount of ICXs in loop
        :param block_number: current block height
        :param period: deposit period in blocks
        """
        # [Sub Task]
        # - Deposits ICX
        # - Calculates Virtual Step
        # - Updates Deposit Data

        if not (self._MIN_DEPOSIT_AMOUNT <= amount <= self._MAX_DEPOSIT_AMOUNT):
            raise InvalidRequestException('Invalid deposit amount')

        if not (self._MIN_DEPOSIT_PERIOD <= period <= self._MAX_DEPOSIT_PERIOD):
            raise InvalidRequestException('Invalid deposit period')

        self._check_score_ownership(context, sender, score_address)

        score_fee_info = self._get_or_create_score_fee(context, score_address)

        # Withdraws from sender's account
        sender_account = self._icx_storage.get_account(context, sender)
        sender_account.withdraw(amount)
        self._icx_storage.put_account(context, sender, sender_account)

        deposit = Deposit(tx_hash, score_address, sender, amount)
        deposit.created = block_number
        deposit.expires = block_number + period
        deposit.virtual_step_issued = \
            self._calculate_virtual_step_issuance(amount, deposit.created, deposit.expires)
        deposit.prev_id = score_fee_info.tail_id

        self._insert_deposit(context, deposit)

        # return (id, SCORE address, sender, amount, period)

    def _insert_deposit(self, context, deposit):
        """
        Inserts deposit information to storage
        """

        score_fee_info = self._get_or_create_score_fee(context, deposit.score_address)

        deposit.prev_id = score_fee_info.tail_id
        self._fee_storage.put_deposit(context, deposit.id, deposit)

        # Link to old last item
        if score_fee_info.tail_id is not None:
            prev_deposit = self._fee_storage.get_deposit(context, score_fee_info.tail_id)
            prev_deposit.next_id = deposit.id
            self._fee_storage.put_deposit(context, prev_deposit.id, prev_deposit)

        # Update head info
        if score_fee_info.head_id is None:
            score_fee_info.head_id = deposit.id

        if score_fee_info.available_head_id_of_virtual_step is None:
            score_fee_info.available_head_id_of_virtual_step = deposit.id

        if score_fee_info.available_head_id_of_deposit is None:
            score_fee_info.available_head_id_of_deposit = deposit.id

        score_fee_info.tail_id = deposit.id
        self._fee_storage.put_score_fee(context, deposit.score_address, score_fee_info)

    def withdraw_fee(self,
                     context: 'IconScoreContext',
                     sender: 'Address',
                     deposit_id: bytes,
                     block_number: int) -> ('Address', int, int):
        """
        Withdraws deposited ICXs from given id.
        It may be paid the penalty if the expiry has not been met.

        :param context: IconScoreContext
        :param sender: msg sender address
        :param deposit_id: deposit id, should be tx hash of deposit transaction
        :param block_number: current block height
        :return: score_address, returning amount of icx, penalty amount of icx
        """
        # [Sub Task]
        # - Checks if the contract period is finished
        # - if the period is not finished, calculates and apply a penalty
        # - Update ICX

        self._check_deposit_id(deposit_id)

        deposit = self._fee_storage.get_deposit(context, deposit_id)

        if deposit is None:
            raise InvalidRequestException('Deposit info not found')

        if deposit.sender != sender:
            raise InvalidRequestException('Invalid sender')

        self._delete_deposit(context, deposit)

        # Deposits to sender's account
        penalty = self._calculate_penalty(
            deposit.deposit_amount, deposit.created, deposit.expires, block_number)

        return_amount = deposit.deposit_amount - deposit.deposit_used - penalty
        if return_amount > 0:
            sender_account = self._icx_storage.get_account(context, sender)
            sender_account.deposit(return_amount)
            self._icx_storage.put_account(context, sender, sender_account)

        return deposit.score_address, return_amount, penalty

    def _delete_deposit(self, context: 'IconScoreContext', deposit: 'Deposit'):
        """
        Deletes deposit information from storage
        """

        # Updates the previous link
        if deposit.prev_id is not None:
            prev_deposit = self._fee_storage.get_deposit(context, deposit.prev_id)
            prev_deposit.next_id = deposit.next_id
            self._fee_storage.put_deposit(context, prev_deposit.id, prev_deposit)

        # Updates the next link
        if deposit.next_id is not None:
            next_deposit = self._fee_storage.get_deposit(context, deposit.next_id)
            next_deposit.prev_id = deposit.prev_id
            self._fee_storage.put_deposit(context, next_deposit.id, next_deposit)

        # Update index info
        score_fee_info = self._fee_storage.get_score_fee(context, deposit.score_address)
        fee_info_changed = False

        if score_fee_info.head_id == deposit.id:
            score_fee_info.head_id = deposit.next_id
            fee_info_changed = True

        if score_fee_info.available_head_id_of_virtual_step == deposit.id:
            score_fee_info.available_head_id_of_virtual_step = deposit.next_id
            fee_info_changed = True

        if score_fee_info.available_head_id_of_deposit == deposit.id:
            score_fee_info.available_head_id_of_deposit = deposit.next_id
            fee_info_changed = True

        if score_fee_info.tail_id == deposit.id:
            score_fee_info.available_head_id_of_deposit = deposit.prev_id
            fee_info_changed = True

        if fee_info_changed:
            # Updates if the information has been changed
            self._fee_storage.put_score_fee(context, deposit.score_address, score_fee_info)

        # Deletes deposit info
        self._fee_storage.delete_deposit(context, deposit.id)

    def get_deposit_info_by_id(self,
                               context: 'IconScoreContext',
                               deposit_id: bytes) -> Deposit:
        """
        Gets the deposit information. Returns None if the deposit from the given id does not exist.

        :param context: IconScoreContext
        :param deposit_id: deposit id, should be tx hash of deposit transaction
        :return: deposit information
        """

        self._check_deposit_id(deposit_id)

        deposit = self._fee_storage.get_deposit(context, deposit_id)

        if deposit is None:
            raise InvalidRequestException('Deposit info not found')

        return deposit

    def can_charge_fee_from_score(self, context: 'IconScoreContext', score_address: 'Address',
                                  block_number: int) -> bool:
        """check if SCORE can charge fee

        :param context:
        :param score_address:
        :param block_number: current block height
        :return: whether SCORE can pay fee
        """
        fee_info: 'Fee' = self._get_or_create_score_fee(context, score_address)

        if not self._is_score_sharing_fee(fee_info):
            return True

        if block_number < fee_info.expires_of_virtual_step and fee_info.available_head_id_of_virtual_step is not None:
            return True

        if block_number < fee_info.expires_of_virtual_step and fee_info.available_head_id_of_virtual_step is not None:
            return True

    def _is_score_sharing_fee(self, score_fee_info: 'Fee') -> bool:
        return score_fee_info.head_id is not None

    # TODO : get_score_info_by_EOA
    def charge_transaction_fee(self,
                               context: 'IconScoreContext',
                               sender: 'Address',
                               to: 'Address',
                               step_price: int,
                               used_step: int,
                               block_number: int) -> Dict['Address', int]:
        """
        Charges fees for the used STEPs.
        It can pay by shared if the msg receiver set to share fees.

        :param context: IconScoreContext
        :param sender: msg sender
        :param to: msg receiver
        :param step_price: current STEP price
        :param used_step: used STEPs
        :param block_number: current block height
        :return Address-used_step dict
        """

        receiver_step = 0

        if to.is_contract:
            receiver_step = self._charge_fee_from_score(
                context, to, step_price, used_step, block_number)

        sender_step = used_step - receiver_step
        self._icx_engine.charge_fee(context, sender, sender_step * step_price)

        if receiver_step > 0:
            detail_step_used = {to: receiver_step}
            if sender_step > 0:
                detail_step_used[sender] = sender_step
            return detail_step_used
        else:
            return {sender: sender_step}

    def _charge_fee_from_score(self,
                               context: 'IconScoreContext',
                               score_address: 'Address',
                               step_price: int,
                               used_step: int,
                               block_number: int) -> int:
        """
        Charges fees from SCORE
        Returns total STEPs SCORE paid
        """

        score_fee_info = self._fee_storage.get_score_fee(context, score_address)
        fee_ratio = score_fee_info.ratio if score_fee_info is not None else 0

        # Amount of STEPs that SCORE will pay
        receiver_step = used_step * fee_ratio // 100

        if receiver_step > 0:
            charged_step, next_head_id_for_virtual_step = self._charge_fee_by_virtual_step(
                context, score_fee_info, receiver_step, block_number)

            icx_required = (receiver_step - charged_step) * step_price
            charged_icx, next_head_id_for_deposit = self._charge_fee_by_deposit(
                context, score_fee_info, icx_required, block_number)

            if icx_required != charged_icx:
                raise InvalidParamsException('Out of deposit balance')

            if score_fee_info.available_head_id_of_virtual_step != next_head_id_for_virtual_step \
                    or score_fee_info.available_head_id_of_deposit != next_head_id_for_deposit:
                # Updates if the information has been changed
                self._fee_storage.put_score_fee(context, score_address, score_fee_info)

        return receiver_step

    def _charge_fee_by_virtual_step(self,
                                    context: 'IconScoreContext',
                                    score_fee_info: 'Fee',
                                    step_required: int,
                                    block_number: int) -> (int, int):
        """
        Charges fees by available virtual STEPs
        Returns total charged amount and next available deposit id
        """

        remaining_required_step = step_required
        last_deposit_id = None

        gen = self._deposit_generator(context, score_fee_info.available_head_id_of_virtual_step)
        for deposit in filter(lambda d: block_number < d.expires, gen):
            available_virtual_step = deposit.available_virtual_step

            if available_virtual_step > 0:
                if remaining_required_step < available_virtual_step:
                    charged_step = remaining_required_step
                else:
                    charged_step = available_virtual_step
                    last_deposit_id = deposit.next_id

                deposit.virtual_step_used += charged_step
                self._fee_storage.put_deposit(context, deposit.id, deposit)

                remaining_required_step -= charged_step

                if remaining_required_step == 0:
                    break

        return step_required - remaining_required_step, last_deposit_id

    def _charge_fee_by_deposit(self,
                               context: 'IconScoreContext',
                               score_fee_info: 'Fee',
                               icx_required: int,
                               block_number: int) -> (int, int):
        """
        Charges fees by available deposit ICXs
        Returns total charged amount and next available deposit id
        """

        remaining_required_icx = icx_required
        last_deposit_id = None

        gen = self._deposit_generator(context, score_fee_info.available_head_id_of_deposit)
        for deposit in filter(lambda d: block_number < d.expires, gen):
            available_deposit = deposit.available_deposit

            if available_deposit > 0:
                if remaining_required_icx < available_deposit:
                    charged_icx = remaining_required_icx
                else:
                    charged_icx = available_deposit
                    last_deposit_id = deposit.next_id

                deposit.deposit_used += charged_icx
                self._fee_storage.put_deposit(context, deposit.id, deposit)

                remaining_required_icx -= charged_icx

                if remaining_required_icx == 0:
                    break

        return icx_required - remaining_required_icx, last_deposit_id

    def _deposit_generator(self, context: 'IconScoreContext', start_id: bytes):
        next_id = start_id
        while next_id is not None:
            deposit = self._fee_storage.get_deposit(context, next_id)
            if deposit is not None:
                next_id = deposit.next_id

                yield deposit
            else:
                break

    def _get_score_deploy_info(self, context, score_address) -> 'IconScoreDeployInfo':
        deploy_info: 'IconScoreDeployInfo' = \
            self._deploy_storage.get_deploy_info(context, score_address)

        if deploy_info is None:
            raise InvalidRequestException('Invalid SCORE')

        return deploy_info

    def _check_score_valid(self, context, score_address) -> None:
        deploy_info = self._get_score_deploy_info(context, score_address)

        assert deploy_info is not None

    def _check_score_ownership(self, context, sender, score_address) -> None:
        deploy_info = self._get_score_deploy_info(context, score_address)

        if deploy_info.owner != sender:
            raise InvalidRequestException('Invalid SCORE owner')

    @staticmethod
    def _check_deposit_id(deposit_id) -> None:
        if deposit_id is None or not isinstance(deposit_id, bytes) or len(deposit_id) != 32:
            raise InvalidRequestException('Invalid deposit ID')

    def _get_or_create_score_fee(
            self, context: 'IconScoreContext', score_address: 'Address') -> 'Fee':
        score_fee_info = self._fee_storage.get_score_fee(context, score_address)
        if score_fee_info is None:
            score_fee_info = Fee()
        return score_fee_info

    @staticmethod
    def _calculate_virtual_step_issuance(deposit_amount: int,
                                         created_at: int,
                                         expires_in: int) -> int:
        assert deposit_amount is not None
        assert created_at is not None
        assert expires_in is not None

        # TODO implement functionality
        return 0

    @staticmethod
    def _calculate_penalty(deposit_amount: int,
                           created_at: int,
                           expires_in: int,
                           block_number: int) -> int:
        assert deposit_amount is not None
        assert created_at is not None
        assert expires_in is not None
        assert block_number is not None

        # TODO implement functionality
        return 0


class FeeHandler:
    """
    Fee Handler
    """

    # For eventlog emitting
    class EventType(IntEnum):
        RATIO = 0
        DEPOSIT = 1
        WITHDRAW = 2

    SIGNATURE_AND_INDEX = [
        ('FeeShareSet(Address,int)', 1),
        ('DepositCreated(bytes,Address,Address,int,int)', 3),
        ('DepositDestroyed(bytes,Address,Address,int,int)', 3)
    ]

    @staticmethod
    def get_signature_and_index_count(event_type: EventType):
        return FeeHandler.SIGNATURE_AND_INDEX[event_type]

    def __init__(self, fee_engine: 'FeeEngine'):
        self.fee_engine = fee_engine

        self.fee_handler = {
            'createDeposit': self._deposit_fee,
            'setRatio': self._set_fee_sharing_ratio,
            'destroyDeposit': self._withdraw_fee,
            'getFeeShare': self._get_fee_sharing_ratio,
            'getDeposit': self._get_deposit_info_by_id,
            'getScoreInfo': self._get_score_fee_info
        }

    def handle_fee_request(self, context: 'IconScoreContext', data: dict):
        """
        Handles fee request(querying or invoking)

        :param context: IconScoreContext
        :param data: data field
        :return:
        """
        converted_data = TypeConverter.convert(data, ParamType.FEE2_PARAMS_DATA)
        method = converted_data['method']

        try:
            handler = self.fee_handler[method]
            params = converted_data.get('params', {})
            return handler(context, **params)
        except KeyError:
            # Case of invoking handler functions with unknown method name
            raise InvalidRequestException(f"Invalid method: {method}")
        except TypeError:
            # Case of invoking handler functions with invalid parameter
            # e.g. 'missing required params' or 'unknown params'
            raise InvalidRequestException(f"Invalid request: parameter error")

    def _deposit_fee(
            self, context: 'IconScoreContext', _score: 'Address', _amount: int, _period: int):

        self.fee_engine.deposit_fee(context, context.tx.hash, context.msg.sender, _score,
                                    _amount, context.block.height, _period)

        event_log_args = [context.tx.hash, _score, context.msg.sender, _amount, _period]
        self._emit_event(context, FeeHandler.EventType.DEPOSIT, event_log_args)

    def _set_fee_sharing_ratio(
            self, context: 'IconScoreContext', _score: 'Address', _ratio: int):

        # return score_address, ratio
        self.fee_engine.set_fee_sharing_ratio(context, context.msg.sender, _score, _ratio)

        event_log_args = [_score, _ratio]
        self._emit_event(context, FeeHandler.EventType.RATIO, event_log_args)

    def _withdraw_fee(self, context: 'IconScoreContext', _id: bytes):
        # return deposit_id, (score_address), context.msg.sender, (return_icx, penalty)
        score_address, return_icx, penalty = self.fee_engine.withdraw_fee(
            context, context.msg.sender, _id, context.block.height)

        event_log_args = [_id, score_address, context.msg.sender, return_icx, penalty]
        self._emit_event(context, FeeHandler.EventType.WITHDRAW, event_log_args)

    def _get_fee_sharing_ratio(self, context: 'IconScoreContext', _score: 'Address'):
        return self.fee_engine.get_fee_sharing_ratio(context, _score)

    def _get_deposit_info_by_id(self, context: 'IconScoreContext', _id: bytes):
        deposit = self.fee_engine.get_deposit_info_by_id(context, _id)
        return deposit.to_dict(to_camel_case)

    def _get_score_fee_info(self, context: 'IconScoreContext', _score: 'Address'):
        score_info = self.fee_engine.get_score_fee_info(context, _score, context.block.height)
        return score_info.to_dict(to_camel_case)

    @staticmethod
    def _emit_event(
            context: 'IconScoreContext', event_type: 'FeeHandler.EventType', event_log_args: list):

        signature, index_count = FeeHandler.get_signature_and_index_count(event_type)

        EventLogEmitter.emit_event_log(
            context, ZERO_SCORE_ADDRESS, signature, event_log_args, index_count)
