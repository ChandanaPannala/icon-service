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

from abc import ABCMeta, abstractmethod
from enum import IntEnum
from typing import Any, TYPE_CHECKING

import msgpack

from .iiss_data_converter import IissDataConverter, TypeTag
from ..base.exception import InvalidParamsException

if TYPE_CHECKING:
    from ..base.address import Address


class IissTxType(IntEnum):
    STAKE = 0
    DELEGATION = 1
    CLAIM = 2
    PREP_REGISTER = 3
    PREP_UNREGISTER = 4
    INVALID = 99


class MsgPackUtil(object):
    @staticmethod
    def dumps(data: Any) -> bytes:
        return msgpack.dumps(data)

    @staticmethod
    def loads(data: bytes) -> list:
        return msgpack.loads(data)


class IissHeader(object):
    _prefix = 'HD'

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


class IissGovernanceVariable(object):
    _prefix = 'gv'

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


class PrepsData(object):
    _prefix = 'prep'

    def __init__(self):
        # key
        self.address: 'Address' = None

        # value
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


class IissTxData(object):
    _prefix = 'TX'

    def __init__(self):
        # key
        self.tx_hash: bytes = None

        # value
        self.address: 'Address' = None
        self.block_height: int = 0
        self.tx_type: 'IissTxType' = IissTxType.INVALID
        self.tx_data: 'IissTx' = None

    def make_key(self) -> bytes:
        prefix: bytes = IissDataConverter.encode(self._prefix)
        tx_hash: bytes = IissDataConverter.encode(self.tx_hash)
        return prefix + tx_hash

    def make_value(self) -> bytes:
        tx_type: 'IissTxType' = self.tx_type
        tx_data: 'IissTx' = self.tx_data

        if isinstance(tx_data, IissTx):
            tx_data_type = tx_data.get_type()
            if tx_type == IissTxType.INVALID:
                tx_type = tx_data_type
            elif tx_type != tx_data_type:
                raise InvalidParamsException(f"Mismatch TxType: {tx_type}")
        else:
            raise InvalidParamsException(f"Invalid TxData: {tx_data}")

        data = [
            IissDataConverter.encode(self.address),
            self.block_height,
            tx_type,
            tx_data.encode()
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
        obj.tx_data: 'IissTx' = IissTxData._covert_tx_data(obj.tx_type, data_list[3])
        return obj

    @staticmethod
    def _covert_tx_data(tx_type: 'IissTxType', data: tuple) -> Any:
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
            raise InvalidParamsException(f"InvalidParams TxType: {tx_type}")


class IissTx(object, metaclass=ABCMeta):
    @abstractmethod
    def get_type(self) -> 'IissTxType':
        pass

    @abstractmethod
    def encode(self) -> list:
        pass

    @staticmethod
    @abstractmethod
    def decode(data: list) -> Any:
        pass


class StakeTx(IissTx):
    def __init__(self):
        # BigInt
        self.stake: int = 0

    def get_type(self) -> 'IissTxType':
        return IissTxType.STAKE

    def encode(self) -> tuple:
        return IissDataConverter.encode_any(self.stake)

    @staticmethod
    def decode(data: tuple) -> 'StakeTx':
        obj = StakeTx()
        obj.stake: int = IissDataConverter.decode_any(data)
        return obj


class DelegationTx(IissTx):
    def __init__(self):
        self.delegation_info: list = []

    def get_type(self) -> 'IissTxType':
        return IissTxType.DELEGATION

    def encode(self) -> tuple:
        data = [x.encode() for x in self.delegation_info]
        return IissDataConverter.encode_any(data)

    @staticmethod
    def decode(data: tuple) -> 'DelegationTx':
        data_list: list = IissDataConverter.decode_any(data)
        obj = DelegationTx()
        obj.delegation_info: list = [DelegationInfo.decode(x) for x in data_list]
        return obj


class DelegationInfo(object):
    def __init__(self):
        self.address: 'Address' = None
        self.ratio: int = None

    def encode(self) -> list:
        return [self.address, self.ratio]

    @staticmethod
    def decode(data: list) -> 'DelegationInfo':
        obj = DelegationInfo()
        obj.address = data[0]
        obj.ratio = data[1]
        return obj


class ClaimTx(IissTx):
    def __init__(self):
        pass

    def get_type(self) -> 'IissTxType':
        return IissTxType.CLAIM

    def encode(self) -> tuple:
        return IissDataConverter.encode_any(None)

    @staticmethod
    def decode(data: tuple) -> 'ClaimTx':
        obj = ClaimTx()
        return obj


class PRepRegisterTx(IissTx):
    def __init__(self):
        pass

    def get_type(self) -> 'IissTxType':
        return IissTxType.PREP_REGISTER

    def encode(self) -> tuple:
        return IissDataConverter.encode_any(None)

    @staticmethod
    def decode(data: tuple) -> 'PRepRegisterTx':
        obj = PRepRegisterTx()
        return obj


class PRepUnregisterTx(IissTx):
    def __init__(self):
        pass

    def get_type(self) -> 'IissTxType':
        return IissTxType.PREP_UNREGISTER

    def encode(self) -> tuple:
        return IissDataConverter.encode_any(None)

    @staticmethod
    def decode(data: tuple) -> 'PRepUnregisterTx':
        obj = PRepUnregisterTx()
        return obj
