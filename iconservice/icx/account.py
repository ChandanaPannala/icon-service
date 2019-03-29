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

from enum import IntFlag
from typing import TYPE_CHECKING, Optional, Any

from ..base.exception import InvalidParamsException
from .coin_part import CoinPartFlag

if TYPE_CHECKING:
    from .coin_part import CoinPart
    from .stake_part import StakePart
    from .delegation_part import DelegationPart
    from ..base.address import Address
    from collections import OrderedDict


class AccountFlag(IntFlag):
    """Account Type
    """
    NONE = 0x0
    COIN = 0x1
    STAKE = 0x2
    COIN_STAKE = COIN|STAKE
    DELEGATION = 0x4


class Account(object):
    def __init__(self, address: 'Address', current_block_height: int):
        self._address: 'Address' = address
        self._current_block_height: int = current_block_height
        self._flag: 'AccountFlag' = AccountFlag.NONE

        self._coin_part: 'CoinPart' = None
        self._stake_part: 'StakePart' = None
        self._delegation_part: 'DelegationPart' = None

    @property
    def flag(self) -> 'AccountFlag':
        return self._flag

    @property
    def address(self):
        return self._address

    @property
    def coin_part(self) -> 'CoinPart':
        return self._coin_part

    @property
    def stake_part(self) -> 'StakePart':
        return self._stake_part

    @property
    def delegation_part(self) -> 'DelegationPart':
        return self._delegation_part

    def init_coin_part_in_icx_storage(self, coin_part: Optional['CoinPart']) -> None:
        self._setter_flag_set(coin_part, AccountFlag.COIN)
        self._coin_part = coin_part

    def init_stake_part_in_icx_storage(self, stake_part: Optional['StakePart']) -> None:
        self._setter_flag_set(stake_part, AccountFlag.STAKE)
        self._stake_part = stake_part

    def init_delegation_part_in_icx_storage(self, delegation_part: Optional['DelegationPart']) -> None:
        self._setter_flag_set(delegation_part, AccountFlag.DELEGATION)
        self._delegation_part = delegation_part

    def _setter_flag_set(self, dest: Any, flag: AccountFlag):
        if dest is None and self.is_flag_on(flag):
            self._flag &= ~flag
        elif not self.is_flag_on(flag):
            self._flag |= flag

    def is_flag_on(self, flag: int) -> bool:
        return self.flag & flag == flag

    def deposit(self, value: int) -> None:
        if not self.is_flag_on(AccountFlag.COIN):
            raise InvalidParamsException('Failed to delegation: InvalidAccount')

        self._update_unstake_state()
        self.coin_part.deposit(value)

    def withdraw(self, value: int) -> None:
        if not self.is_flag_on(AccountFlag.COIN):
            raise InvalidParamsException('Failed to delegation: InvalidAccount')

        self._update_unstake_state()
        self.coin_part.withdraw(value)

    def _update_unstake_state(self):
        if not self.coin_part.is_coin_flag_on(CoinPartFlag.HAS_UNSTAKE):
            return

        if not self.is_flag_on(AccountFlag.STAKE):
            raise InvalidParamsException('Failed to coin: InvalidAccount')

        if self._current_block_height > self.unstake_block_height:
            balance: int = self.stake_part.payback_unstake()
            if balance > 0:
                self.coin_part.coin_flag_disable(CoinPartFlag.HAS_UNSTAKE)
                self.coin_part.deposit(balance)

    @property
    def balance(self) -> int:
        balance = 0

        if self.is_flag_on(AccountFlag.COIN):
            balance = self.coin_part.balance

        if self.is_flag_on(AccountFlag.STAKE):
            if self._current_block_height > self.stake_part.unstake_block_height:
                balance += self.stake_part.unstake
        return balance

    @property
    def stake(self) -> int:
        if not self.is_flag_on(AccountFlag.STAKE):
            return 0
        return self.stake_part.stake

    @property
    def unstake(self) -> int:
        if not self.is_flag_on(AccountFlag.STAKE):
            return 0
        return self.stake_part.unstake

    @property
    def unstake_block_height(self) -> int:
        if not self.is_flag_on(AccountFlag.STAKE):
            return self._current_block_height
        return self.stake_part.unstake_block_height

    @property
    def delegated_amount(self) -> int:
        if not self.is_flag_on(AccountFlag.STAKE):
            return 0
        return self.delegation_part.delegated_amount

    @property
    def delegations(self) -> Optional['OrderedDict']:
        if not self.is_flag_on(AccountFlag.STAKE):
            return None
        return self.delegation_part.delegations

    def set_stake(self, value: int, unstake_lock_period: int) -> None:
        if not self.is_flag_on(AccountFlag.COIN | AccountFlag.STAKE):
            raise InvalidParamsException('Failed to stake: InvalidAccount')

        if not isinstance(value, int) or value < 0:
            raise InvalidParamsException('Failed to stake: value is not int type or value < 0')

        total: int = self.balance + self.stake

        if total < value:
            raise InvalidParamsException('Failed to stake: total < stake')

        offset: int = value - self.stake

        if offset == 0:
            return
        elif offset > 0:
            self.coin_part.withdraw(value)
            self.stake_part.update_stake(abs(offset))
        else:
            unlock_block_height: int = self._current_block_height + unstake_lock_period
            self.coin_part.coin_flag_enable(CoinPartFlag.HAS_UNSTAKE)
            self.stake_part.update_unstake(unlock_block_height, abs(offset))

    def delegate(self, target: 'Account', value: int) -> bool:
        if not self.is_flag_on(AccountFlag.DELEGATION) or not target.is_flag_on(AccountFlag.DELEGATION):
            raise InvalidParamsException('Failed to delegation: InvalidAccount')
        return self.delegation_part.update_delegation(target.delegation_part, value)

    def __eq__(self, other) -> bool:
        """operator == overriding

        :param other: (CoinPart)
        """
        return isinstance(other, Account) \
               and self.address == other.address \
               and self._flag == other.flag \
               and self._coin_part == other.coin_part \
               and self.stake_part == other.stake_part \
               and self.delegation_part == other.delegation_part

    def __ne__(self, other) -> bool:
        """operator != overriding

        :param other: (CoinPart)
        """
        return not self.__eq__(other)
