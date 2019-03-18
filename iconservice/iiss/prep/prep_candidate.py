# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


from enum import IntEnum, unique
from typing import TYPE_CHECKING

from ...base.msgpack_util import MsgPackConverter, TypeTag
from ...base.exception import InvalidParamsException
from ..iiss_data_converter import IissDataConverter

if TYPE_CHECKING:
    from ...base.address import Address


@unique
class Version(IntEnum):
    BASE = 0


class PrepCandidateRegInfo(object):
    """PrepCandidate Register Info class
    Contains information of the PrepCandidate indicated by address.
    """

    _prefix = 'prepri'

    def __init__(self) -> None:
        """Constructor
        """
        # key
        self.address: 'Address' = None

        # value
        self.network_info: str = ""
        self.name: str = ""
        self.url: str = ""
        self.block_height: int = 0
        self.timestamp: int = 0
        self.gv: 'GovernanceVariables' = None

    def make_key(self) -> bytes:
        prefix: bytes = IissDataConverter.encode(self._prefix)
        address: bytes = IissDataConverter.encode(self.address)
        return prefix + address

    def to_bytes(self) -> bytes:
        """Convert PrepCandidate object to bytes

        :return: data including information of PrepCandidate object
        """

        version: int = Version.BASE

        data = [
            version,
            IissDataConverter.encode(self.network_info),
            IissDataConverter.encode(self.name),
            IissDataConverter.encode(self.url),
            self.block_height,
            self.timestamp,
            self.gv.encode()
        ]
        return IissDataConverter.dumps(data)

    @staticmethod
    def from_bytes(address: 'Address', data: bytes) -> 'PrepCandidateRegInfo':
        """Create PrepCandidate object from bytes data

        :param address:
        :param data: (bytes) bytes data including PrepCandidate information
        :return: (PrepCandidate) PrepCandidate object
        """

        data_list: list = IissDataConverter.loads(data)
        version: int = data_list[0]
        if version == Version.BASE:
            obj = PrepCandidateRegInfo()
            obj.address: 'Address' = address
            obj.network_info: str = IissDataConverter.decode(TypeTag.STRING, data_list[1])
            obj.name: str = IissDataConverter.decode(TypeTag.STRING, data_list[2])
            obj.url: str = IissDataConverter.decode(TypeTag.STRING, data_list[3])
            obj.block_height: int = data_list[4]
            obj.timestamp: int = data_list[5]
            obj.gv: 'GovernanceVariables' = GovernanceVariables.decode(data_list[6])
            return obj
        else:
            raise InvalidParamsException(f"Invalid PrepCandidateRegInfo version: {version}")


class GovernanceVariables(object):
    def __init__(self):
        self.icxPrice: int = 0
        self.incentiveRep: int = 0

    def encode(self) -> list:
        data = [
            MsgPackConverter.encode(self.icxPrice),
            MsgPackConverter.encode(self.incentiveRep)
        ]
        return data

    @staticmethod
    def decode(data: list) -> 'GovernanceVariables':
        obj = GovernanceVariables()
        obj.icxPrice: int = MsgPackConverter.decode(TypeTag.INT, data[0])
        obj.incentiveRep: int = MsgPackConverter.decode(TypeTag.INT, data[1])
        return obj

