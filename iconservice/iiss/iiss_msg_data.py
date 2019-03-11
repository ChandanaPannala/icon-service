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

from enum import IntEnum
from typing import Any, TYPE_CHECKING, Tuple

import msgpack

from .iiss_data_converter import IissDataConverter, TypeTag

if TYPE_CHECKING:
    from ..base.address import Address


class IissTxType(IntEnum):
    STAKE = 0
    DELEGATION = 1
    CLAIM = 2
    PREP_REGISTER = 2
    PREP_UNREGISTER = 3


class MsgPackUtil:
    @staticmethod
    def dumps(data: Any) -> bytes:
        return msgpack.dumps(data)

    @staticmethod
    def loads(data: bytes) -> list:
        return msgpack.loads(data)


class IissHeader:
    _prefix = b'HX'

    def __init__(self):
        self.version: int = 0
        self.block_height: int = 0

    def make_key(self) -> bytes:
        return IissDataConverter.encode(self._prefix)

    def make_value(self) -> bytes:
        data = [
            self.version,
            self.block_height
        ]

        return MsgPackUtil.dumps(data)

    @staticmethod
    def get_value(data: bytes) -> 'IissHeader':
        data_list: list = MsgPackUtil.loads(data)
        obj = IissHeader()
        obj.version: int = data_list[0]
        obj.block_height: int = data_list[1]
        return obj


class IissGovernanceVariable:
    _prefix = b'gv'

    def __init__(self):
        self.icx_price: int = 0
        self.incentive_rep: int = 0

    def make_key(self) -> bytes:
        return IissDataConverter.encode(self._prefix)

    def make_value(self) -> bytes:
        data = [
            self.icx_price,
            self.incentive_rep
        ]
        return MsgPackUtil.dumps(data)

    @staticmethod
    def get_value(data: bytes) -> 'IissGovernanceVariable':
        data_list: list = MsgPackUtil.loads(data)
        obj = IissGovernanceVariable()
        obj.icx_price: int = data_list[0]
        obj.incentive_rep: int = data_list[1]
        return obj


class PrepsData:
    _prefix = b'prep'

    def __init__(self):
        self.address: 'Address' = None

        self.block_generate_count: int = 0
        self.block_validate_count: int = 0

    def make_key(self) -> bytes:
        prefix: bytes = IissDataConverter.encode(self._prefix)
        address: bytes = IissDataConverter.encode(self.address)
        return prefix + address

    def make_value(self) -> bytes:
        data = [
            self.block_generate_count,
            self.block_validate_count
        ]
        return MsgPackUtil.dumps(data)

    @staticmethod
    def get_value(address: 'Address', data: bytes) -> 'PrepsData':
        data_list: list = MsgPackUtil.loads(data)
        obj = PrepsData()
        obj.address: Address = address
        obj.block_generate_count: int = data_list[0]
        obj.block_validate_count: int = data_list[1]
        return obj


class IissTxData:
    _prefix = b'TX'

    def __init__(self):
        self.tx_hash: bytes = None

        self.address: 'Address' = None
        self.block_height: int = 0
        self.tx_type: 'IissTxType' = IissTxType.STAKE
        self.tx_data: Any = None

    def make_key(self) -> bytes:
        prefix: bytes = self._prefix
        tx_hash: bytes = self.tx_hash
        return prefix + tx_hash

    def make_value(self) -> bytes:
        data = [
            IissDataConverter.encode(self.address),
            self.block_height,
            self.tx_type,
            self.tx_data.encode()
        ]
        return MsgPackUtil.dumps(data)

    @staticmethod
    def get_value(tx_hash: bytes, data: bytes) -> 'IissTxData':
        data_list: list = MsgPackUtil.loads(data)
        obj = IissTxData()
        obj.tx_hash: bytes = tx_hash
        obj.address: 'Address' = IissDataConverter.decode(TypeTag.ADDRESS, data_list[0])
        obj.block_height: int = data_list[1]
        obj.tx_type: 'IissTxType' = IissTxType(data_list[2])
        obj.tx_data: Any = IissTxData._covert_tx_data(obj.tx_type, data_list[3])
        return obj

    @staticmethod
    def _covert_tx_data(tx_type: 'IissTxType', data: bytes) -> Any:
        if tx_type == IissTxType.STAKE:
            return StakeTx.decode(data)
        elif tx_type == IissTxType.DELEGATION:
            return DelegationTx.decode(data)
        elif tx_type == IissTxType.CLAIM:
            return ClaimTx.decode(data)
        elif tx_type == IissTxType.PREP_REGISTER:
            return PRepRegisterTx.decode(data)
        elif tx_type == IissTxType.PREP_UNREGISTER:
            return PRepUnregisterTx.decode(data)
        else:
            pass


class StakeTx:
    def __init__(self):
        # BigInt
        self.stake: int = 0

    def encode(self) -> bytes:
        tag, data = IissDataConverter.encode_any(self.stake)
        return MsgPackUtil.dumps([tag, data])

    @staticmethod
    def decode(data: bytes) -> 'StakeTx':
        tag, data = MsgPackUtil.loads(data)
        obj = StakeTx()
        obj.stake: int = IissDataConverter.decode(tag, data)
        return obj


class DelegationTx:
    def __init__(self):
        self.delegation_info: 'DelegationInfo' = None

    def encode(self) -> bytes:
        tag, data = self.delegation_info.encode()
        return MsgPackUtil.dumps([tag, data])

    @staticmethod
    def decode(data: bytes) -> 'DelegationTx':
        tag, data = MsgPackUtil.loads(data)
        obj = DelegationTx()
        obj.delegation_info: 'DelegationInfo' = DelegationInfo.decode(data)
        return obj


class DelegationInfo:
    def __init__(self):
        self.address_list: list = []
        self.ratio_list: list = []

    def encode(self) -> Tuple:
        data = []
        for x, y in zip(self.address_list, self.ratio_list):
            address_bytes: 'bytes' = IissDataConverter.encode(x)
            data.append(address_bytes)
            data.append(y)

        return TypeTag.LIST, data

    @staticmethod
    def decode(data: list) -> 'DelegationInfo':
        obj = DelegationInfo()

        for index, data in enumerate(data):
            if index % 2 == 0:
                address: 'Address' = IissDataConverter.decode(TypeTag.ADDRESS, data)
                obj.address_list.append(address)
            else:
                obj.ratio_list.append(data)
        return obj


class ClaimTx:
    def __init__(self):
        pass

    def encode(self) -> bytes:
        tag, data = IissDataConverter.encode_any(None)
        return MsgPackUtil.dumps([tag, data])

    @staticmethod
    def decode(data: bytes) -> 'ClaimTx':
        data_list: list = MsgPackUtil.loads(data)
        obj = ClaimTx()
        return obj


class PRepRegisterTx:
    def __init__(self):
        pass

    def encode(self) -> bytes:
        tag, data = IissDataConverter.encode_any(None)
        return MsgPackUtil.dumps([tag, data])

    @staticmethod
    def decode(data: bytes) -> 'PRepRegisterTx':
        data_list: list = MsgPackUtil.loads(data)
        obj = PRepRegisterTx()
        return obj


class PRepUnregisterTx:
    def __init__(self):
        pass

    def encode(self) -> bytes:
        tag, data = IissDataConverter.encode_any(None)
        return MsgPackUtil.dumps([tag, data])

    @staticmethod
    def decode(data: bytes) -> 'PRepUnregisterTx':
        data_list: list = MsgPackUtil.loads(data)
        obj = PRepUnregisterTx()
        return obj
