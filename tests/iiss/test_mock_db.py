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
import plyvel
import unittest
from typing import TYPE_CHECKING

from iconservice.iiss.iiss_msg_data import IissHeader, IissGovernanceVariable, PrepsData, IissTxData, IissTxType, StakeTx, \
    DelegationTx, DelegationInfo, ClaimTx, PRepRegisterTx, PRepUnregisterTx
from tests import create_address

if TYPE_CHECKING:
    from iconservice.base.address import Address


class TestIissData(unittest.TestCase):
    def test_make_mock_db(self):
        db = plyvel.DB('./mock_db', create_if_missing=True)

        h = IissHeader()
        h.version = 1
        h.block_height = 1

        key: bytes = h.make_key()
        value: bytes = h.make_value()
        db.put(key, value)

        print("===IISS_HEADER===")
        print(f"version: {h.version}")
        print(f"block_height: {h.block_height}")
        print(f"key: {key}")
        print(f"value: {value}")

        gv = IissGovernanceVariable()
        gv.icx_price = 10
        gv.incentive_rep = 10

        key: bytes = gv.make_key()
        value: bytes = gv.make_value()
        db.put(key, value)

        print("===IISS_GOVERNANCE_VARIABLE===")
        print(f"version: {gv.icx_price}")
        print(f"block_height: {gv.incentive_rep}")
        print(f"key: {key}")
        print(f"value: {value}")

        p = PrepsData()
        p.address = create_address(data=b'addr1')
        p.block_generate_count = 3
        p.block_validate_count = 10

        key: bytes = p.make_key()
        value: bytes = p.make_value()
        db.put(key, value)

        print("===PREPS_DATA===")
        print(f"address: {p.address}")
        print(f"block_generate_count: {p.block_generate_count}")
        print(f"block_validate_count: {p.block_validate_count}")
        print(f"key: {key}")
        print(f"value: {value}")

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash1'
        tx.address: 'Address' = create_address(data=b'addr2')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.STAKE
        tx.tx_data: 'StakeTx' = StakeTx()
        tx.tx_data.stake: int = 10 ** 30

        key: bytes = tx.make_key()
        value: bytes = tx.make_value()
        db.put(key, value)

        print("===IISS_TX_DATA-1===")
        print(f"tx_hash: {tx.tx_hash}")
        print(f"address: {tx.address}")
        print(f"block_height: {tx.block_height}")
        print(f"tx_type: {tx.tx_type}")
        print(f"stake: {tx.tx_data.stake}")
        print(f"key: {key}")
        print(f"value: {value}")

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash2'
        tx.address: 'Address' = create_address(data=b'addr3')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.DELEGATION
        tx.tx_data: 'DelegationTx' = DelegationTx()
        tx.tx_data.delegation_info = DelegationInfo()
        tx.tx_data.delegation_info.address_list.append(create_address(data=b'addr4'))
        tx.tx_data.delegation_info.ratio_list.append(10)
        tx.tx_data.delegation_info.address_list.append(create_address(data=b'addr5'))
        tx.tx_data.delegation_info.ratio_list.append(20)

        key: bytes = tx.make_key()
        value: bytes = tx.make_value()
        db.put(key, value)

        print("===IISS_TX_DATA-2===")
        print(f"tx_hash: {tx.tx_hash}")
        print(f"address: {tx.address}")
        print(f"block_height: {tx.block_height}")
        print(f"tx_type: {tx.tx_type}")

        p_data = [tx.tx_data.delegation_info.address_list[0],
                  tx.tx_data.delegation_info.ratio_list[0],
                  tx.tx_data.delegation_info.address_list[1],
                  tx.tx_data.delegation_info.ratio_list[1]]

        print(f"delegate: {p_data}")
        print(f"key: {key}")
        print(f"value: {value}")

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash3'
        tx.address: 'Address' = create_address(data=b'addr6')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.CLAIM
        tx.tx_data: 'ClaimTx' = ClaimTx()

        key: bytes = tx.make_key()
        value: bytes = tx.make_value()
        db.put(key, value)

        print("===IISS_TX_DATA-3===")
        print(f"tx_hash: {tx.tx_hash}")
        print(f"address: {tx.address}")
        print(f"block_height: {tx.block_height}")
        print(f"tx_type: {tx.tx_type}")
        print(f"data: {tx.tx_data}")
        print(f"key: {key}")
        print(f"value: {value}")

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash4'
        tx.address: 'Address' = create_address(data=b'addr7')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.PREP_REGISTER
        tx.tx_data: 'PRepRegisterTx' = PRepRegisterTx()

        key: bytes = tx.make_key()
        value: bytes = tx.make_value()
        db.put(key, value)

        print("===IISS_TX_DATA-4===")
        print(f"tx_hash: {tx.tx_hash}")
        print(f"address: {tx.address}")
        print(f"block_height: {tx.block_height}")
        print(f"tx_type: {tx.tx_type}")
        print(f"data: {tx.tx_data}")
        print(f"key: {key}")
        print(f"value: {value}")

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash5'
        tx.address: 'Address' = create_address(data=b'addr8')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.PREP_REGISTER
        tx.tx_data: 'PRepUnregisterTx' = PRepUnregisterTx()

        key: bytes = tx.make_key()
        value: bytes = tx.make_value()
        db.put(key, value)

        print("===IISS_TX_DATA-5===")
        print(f"tx_hash: {tx.tx_hash}")
        print(f"address: {tx.address}")
        print(f"block_height: {tx.block_height}")
        print(f"tx_type: {tx.tx_type}")
        print(f"data: {tx.tx_data}")
        print(f"key: {key}")
        print(f"value: {value}")

    def test_load_mock_db(self):
        db = plyvel.DB('./mock_db', create_if_missing=True)

        h = IissHeader()
        h.version = 1
        h.block_height = 1

        key: bytes = h.make_key()
        value = db.get(key)
        ret_h: 'IissHeader' = h.get_value(value)

        self.assertEqual(h.version, ret_h.version)
        self.assertEqual(h.block_height, ret_h.block_height)

        gv = IissGovernanceVariable()
        gv.icx_price = 10
        gv.incentive_rep = 10

        key: bytes = gv.make_key()
        value = db.get(key)
        ret_gv: 'IissGovernanceVariable' = gv.get_value(value)

        self.assertEqual(gv.icx_price, ret_gv.icx_price)
        self.assertEqual(gv.incentive_rep, ret_gv.incentive_rep)

        p = PrepsData()
        p.address = create_address(data=b'addr1')
        p.block_generate_count = 3
        p.block_validate_count = 10

        key: bytes = p.make_key()
        value = db.get(key)
        ret_p: 'PrepsData' = p.get_value(p.address, value)

        self.assertEqual(p.block_generate_count, ret_p.block_generate_count)
        self.assertEqual(p.block_validate_count, ret_p.block_validate_count)

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash1'
        tx.address: 'Address' = create_address(data=b'addr2')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.STAKE
        tx.tx_data: 'StakeTx' = StakeTx()
        tx.tx_data.stake: int = 10 ** 30

        key: bytes = tx.make_key()
        value = db.get(key)
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, value)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)

        self.assertEqual(tx.tx_data.stake, ret_tx.tx_data.stake)

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash2'
        tx.address: 'Address' = create_address(data=b'addr3')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.DELEGATION
        tx.tx_data: 'DelegationTx' = DelegationTx()
        tx.tx_data.delegation_info = DelegationInfo()
        tx.tx_data.delegation_info.address_list.append(create_address(data=b'addr4'))
        tx.tx_data.delegation_info.ratio_list.append(10)
        tx.tx_data.delegation_info.address_list.append(create_address(data=b'addr5'))
        tx.tx_data.delegation_info.ratio_list.append(20)

        key: bytes = tx.make_key()
        value = db.get(key)
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, value)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)

        self.assertEqual(tx.tx_data.delegation_info.address_list[0], ret_tx.tx_data.delegation_info.address_list[0])
        self.assertEqual(tx.tx_data.delegation_info.address_list[1], ret_tx.tx_data.delegation_info.address_list[1])
        self.assertEqual(tx.tx_data.delegation_info.ratio_list[0], ret_tx.tx_data.delegation_info.ratio_list[0])
        self.assertEqual(tx.tx_data.delegation_info.ratio_list[1], ret_tx.tx_data.delegation_info.ratio_list[1])

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash3'
        tx.address: 'Address' = create_address(data=b'addr6')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.CLAIM
        tx.tx_data: 'ClaimTx' = ClaimTx()

        key: bytes = tx.make_key()
        value = db.get(key)
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, value)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash4'
        tx.address: 'Address' = create_address(data=b'addr7')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.PREP_REGISTER
        tx.tx_data: 'PRepRegisterTx' = PRepRegisterTx()

        key: bytes = tx.make_key()
        value = db.get(key)
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, value)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)

        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash5'
        tx.address: 'Address' = create_address(data=b'addr8')
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.PREP_REGISTER
        tx.tx_data: 'PRepUnregisterTx' = PRepUnregisterTx()

        key: bytes = tx.make_key()
        value = db.get(key)
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, value)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)


if __name__ == '__main__':
    unittest.main()
