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
from typing import TYPE_CHECKING

from ..base.msgpack_util import MsgPackConverter, TypeTag

if TYPE_CHECKING:
    from ..base.address import Address


class DelegationPart(object):
    prefix = b"aod|"

    def __init__(self, address: 'Address'):
        self._address: 'Address' = address
        self._delegated_amount: int = 0
        self._delegations: OrderedDict = OrderedDict()

    @staticmethod
    def make_key(address: 'Address'):
        return DelegationPart.prefix + MsgPackConverter.encode(address)

    @property
    def address(self) -> 'Address':
        return self._address

    @property
    def delegated_amount(self) -> int:
        return self._delegated_amount

    @delegated_amount.setter
    def delegated_amount(self, delegated_amount: int):
        self._delegated_amount = delegated_amount

    @property
    def delegations(self) -> OrderedDict:
        return self._delegations

    @staticmethod
    def from_bytes(buf: bytes, address: 'Address') -> 'DelegationPart':
        """Create DelegationPart object from bytes data

        :param buf: (bytes) bytes data including DelegationPart information
        :param address:
        :return: (DelegationPart) DelegationPart object
        """

        data: list = MsgPackConverter.loads(buf)
        version = MsgPackConverter.decode(TypeTag.INT, data[0])

        obj = DelegationPart(address)
        obj._delegated_amount: int = MsgPackConverter.decode(TypeTag.INT, data[1])

        delegations: list = data[2]
        for i in range(0, len(delegations), 2):
            info = DelegationPartInfo()
            info.address = MsgPackConverter.decode(TypeTag.ADDRESS, delegations[i])
            info.value = MsgPackConverter.decode(TypeTag.INT, delegations[i + 1])
            obj.delegations[info.address] = info
        return obj

    def to_bytes(self) -> bytes:
        """Convert Account of Stake object to bytes

        :return: data including information of AccountOfDelegation object
        """

        version = 0
        data = [MsgPackConverter.encode(version),
                MsgPackConverter.encode(self.delegated_amount)]
        delegations = []
        for info in self.delegations.values():
            delegations.append(MsgPackConverter.encode(info.address))
            delegations.append(MsgPackConverter.encode(info.value))
        data.append(delegations)

        return MsgPackConverter.dumps(data)

    def update_delegation(self, to: 'DelegationPart', value: int) -> bool:
        info: 'DelegationPartInfo' = self._delegations.get(to.address)

        if info is None:
            if value == 0:
                ret = False
            else:
                info: 'DelegationPartInfo' = DelegationPart.create_delegation(to.address, value)
                self._delegations[to.address] = info
                to.delegated_amount += value
                ret = True
        else:
            prev_value: int = info.value
            offset: int = value - prev_value

            if offset != 0:
                info.value += offset
                to.delegated_amount += offset
                ret = True
            else:
                ret = False

            if info.value == 0:
                del self._delegations[info.address]
        return ret

    @staticmethod
    def create_delegation(address: 'Address', value: int) -> 'DelegationPartInfo':
        d = DelegationPartInfo()
        d.address: 'Address' = address
        d.value: int = value
        return d

    def __eq__(self, other) -> bool:
        """operator == overriding

        :param other: (AccountOfDelegation)
        """

        return isinstance(other, DelegationPart) \
               and self._address == other.address \
               and self._delegated_amount == other.delegated_amount \
               and self._delegations == other.delegations

    def __ne__(self, other) -> bool:
        """operator != overriding

        :param other: (AccountOfDelegation)
        """
        return not self.__eq__(other)


class DelegationPartInfo(object):
    def __init__(self):
        self.address: 'Address' = None
        self.value: int = 0

    def __eq__(self, other) -> bool:
        """operator == overriding

        :param other: (AccountDelegationInfo)
        """
        return isinstance(other, DelegationPartInfo) \
               and self.address == other.address \
               and self.value == other.value

    def __ne__(self, other) -> bool:
        """operator != overriding

        :param other: (AccountDelegationInfo)
        """
        return not self.__eq__(other)

    def to_dict(self):
        return {
            "address": self.address,
            "value": self.value
        }