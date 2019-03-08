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

from enum import IntEnum
from typing import Tuple, Any, Union

from ..icon_constant import CHARSET_ENCODING
from ..utils import int_to_bytes, bytes_to_int
from ..base.address import AddressPrefix, Address
from .ipc.proxy import Codec


class TypeTag(IntEnum):
    NIL = 0
    DICT = 1
    LIST = 2
    BYTES = 3
    STRING = 4

    CUSTOM = 10
    INT = CUSTOM + 1
    ADDRESS = CUSTOM


class DataType(IntEnum):
    INTEGER = 1
    STRING = 2
    BYTES = 3
    BOOL = 4
    ADDRESS = 5
    LIST = 6
    DICT = 7


def address_to_bytes(addr: 'Address') -> bytes:
    prefix_byte = b''
    addr_bytes = addr.to_bytes()
    if addr.prefix == AddressPrefix.EOA:
        prefix_byte = int_to_bytes(addr.prefix.value)
    return prefix_byte + addr_bytes


def bytes_to_address(data: bytes) -> 'Address':
    prefix = AddressPrefix(data[0])
    return Address(prefix, data[1:])


class IissCodec(Codec):
    def encode(self, obj) -> Tuple[int, bytes]:
        if isinstance(obj, Address):
            return TypeTag.ADDRESS, address_to_bytes(obj)
        raise Exception

    def decode(self, t: int, b: bytes) -> Any:
        if t == TypeTag.ADDRESS:
            return bytes_to_address(b)
        else:
            raise Exception(f"UnknownType: {type(t)}")


class IissDataConverter:
    codec: 'Codec' = IissCodec()

    @classmethod
    def decode(cls, tag: int, val: bytes) -> 'Any':
        if tag == TypeTag.BYTES:
            return val
        elif tag == TypeTag.STRING:
            return val.decode(CHARSET_ENCODING)
        elif tag == TypeTag.INT:
            return bytes_to_int(val)
        else:
            return cls.codec.decode(tag, val)

    @classmethod
    def encode(cls, o: Any) -> bytes:
        if o is None:
            return bytes([])
        if isinstance(o, int):
            return int_to_bytes(o)
        elif isinstance(o, str):
            return o.encode(CHARSET_ENCODING)
        elif isinstance(o, bytes):
            return o
        elif isinstance(o, bool):
            if o:
                return b'\x01'
            else:
                return b'\x00'
        else:
            t, v = cls.codec.encode(o)
            return v

    @classmethod
    def decode_any(cls, to: Tuple) -> Any:
        tag: int = to[0]
        val: Union[bytes, dict, list] = to[1]
        if tag == TypeTag.NIL:
            return None
        elif tag == TypeTag.DICT:
            obj = {}
            for k, v in val.items():
                if isinstance(k, bytes):
                    k = k.decode(CHARSET_ENCODING)
                obj[k] = cls.decode_any(v)
            return obj
        elif tag == TypeTag.LIST:
            obj = []
            for v in val:
                obj.append(cls.decode_any(v))
            return obj
        else:
            return cls.decode(tag, val)

    @classmethod
    def encode_any(cls, o: Any) -> Tuple[int, Any]:
        if o is None:
            return TypeTag.NIL, b''
        elif isinstance(o, dict):
            m = {}
            for k, v in o.items():
                m[k] = cls.encode_any(v)
            return TypeTag.DICT, m
        elif isinstance(o, list) or isinstance(o, tuple):
            lst = []
            for v in o:
                lst.append(cls.encode_any(v))
            return TypeTag.LIST, lst
        elif isinstance(o, bytes):
            return TypeTag.BYTES, o
        elif isinstance(o, str):
            return TypeTag.STRING, o.encode(CHARSET_ENCODING)
        elif isinstance(o, int):
            return TypeTag.INT, int_to_bytes(o)
        else:
            return cls.codec.encode(o)
