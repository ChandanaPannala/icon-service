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
from tests import create_address, rmtree

if TYPE_CHECKING:
    from iconservice.base.address import Address


class TestIissDataUsingLevelDB(unittest.TestCase):
    db_path: str = './mock_db'

    def setUp(self):
        self.db = plyvel.DB('./mock_db', create_if_missing=True)
        self.debug = False

        self.iiss_header: 'IissHeader' = IissHeader()
        self.iiss_header.version = 10
        self.iiss_header.block_height = 20

        self.iiss_gv: 'IissGovernanceVariable' = IissGovernanceVariable()
        self.iiss_gv.icx_price = 10
        self.iiss_gv.incentive_rep = 30

        self.iiss_prep: 'PrepsData' = PrepsData()
        self.iiss_prep.address = create_address(data=b'addr1')
        self.iiss_prep.block_generate_count = 3
        self.iiss_prep.block_validate_count = 10

        self.tx_stake: 'IissTxData' = IissTxData()
        self.tx_stake.tx_hash: bytes = b'tx_hash1'
        self.tx_stake.address: 'Address' = create_address(data=b'addr2')
        self.tx_stake.block_height: int = 10 ** 3
        self.tx_stake.tx_type: 'IissTxType' = IissTxType.STAKE
        self.tx_stake.tx_data: 'StakeTx' = StakeTx()
        self.tx_stake.tx_data.stake: int = 10 ** 18

        self.tx_delegate: 'IissTxData' = IissTxData()
        self.tx_delegate.tx_hash: bytes = b'tx_hash2'
        self.tx_delegate.address: 'Address' = create_address(data=b'addr3')
        self.tx_delegate.block_height: int = 10 ** 3
        self.tx_delegate.tx_type: 'IissTxType' = IissTxType.DELEGATION
        self.tx_delegate.tx_data: 'DelegationTx' = DelegationTx()

        delegate_info: 'DelegationInfo' = DelegationInfo()
        delegate_info.address = create_address(data=b'addr4')
        delegate_info.ratio = 10
        self.tx_delegate.tx_data.delegation_info.append(delegate_info)

        delegate_info: 'DelegationInfo' = DelegationInfo()
        delegate_info.address = create_address(data=b'addr5')
        delegate_info.ratio = 20
        self.tx_delegate.tx_data.delegation_info.append(delegate_info)

        self.tx_claim: 'IissTxData' = IissTxData()
        self.tx_claim.tx_hash: bytes = b'tx_hash3'
        self.tx_claim.address: 'Address' = create_address(data=b'addr6')
        self.tx_claim.block_height: int = 10 ** 3
        self.tx_claim.tx_type: 'IissTxType' = IissTxType.CLAIM
        self.tx_claim.tx_data: 'ClaimTx' = ClaimTx()

        self.tx_prep_reg: 'IissTxData' = IissTxData()
        self.tx_prep_reg.tx_hash: bytes = b'tx_hash4'
        self.tx_prep_reg.address: 'Address' = create_address(data=b'addr7')
        self.tx_prep_reg.block_height: int = 10 ** 3
        self.tx_prep_reg.tx_type: 'IissTxType' = IissTxType.PREP_REGISTER
        self.tx_prep_reg.tx_data: 'PRepRegisterTx' = PRepRegisterTx()

        self.tx_prep_un_reg: 'IissTxData' = IissTxData()
        self.tx_prep_un_reg.tx_hash: bytes = b'tx_hash5'
        self.tx_prep_un_reg.address: 'Address' = create_address(data=b'addr8')
        self.tx_prep_un_reg.block_height: int = 10 ** 3
        self.tx_prep_un_reg.tx_type: 'IissTxType' = IissTxType.PREP_UNREGISTER
        self.tx_prep_un_reg.tx_data: 'PRepUnregisterTx' = PRepUnregisterTx()

    def tearDown(self):
        rmtree(self.db_path)
        pass

    def test_iiss_data_using_level_db(self):
        self._dump_mock_db()
        self._load_mock_db()

    def test_iiss_header_data(self):
        data: bytes = self.iiss_header.make_value()
        ret_h: 'IissHeader' = self.iiss_header.get_value(data)

        self.assertEqual(self.iiss_header.version, ret_h.version)
        self.assertEqual(self.iiss_header.block_height, ret_h.block_height)

    def test_iiss_governance_variable_data(self):
        data: bytes = self.iiss_gv.make_value()
        ret_gv: 'IissGovernanceVariable' = self.iiss_gv.get_value(data)

        self.assertEqual(self.iiss_gv.icx_price, ret_gv.icx_price)
        self.assertEqual(self.iiss_gv.incentive_rep, ret_gv.incentive_rep)

    def test_preps_data(self):
        data: bytes = self.iiss_prep.make_value()
        ret_p: 'PrepsData' = self.iiss_prep.get_value(self.iiss_prep.address, data)

        self.assertEqual(self.iiss_prep.block_generate_count, ret_p.block_generate_count)
        self.assertEqual(self.iiss_prep.block_validate_count, ret_p.block_validate_count)

    def test_iiss_tx_data_stake(self):
        data: bytes = self.tx_stake.make_value()
        ret_tx: 'IissTxData' = self.tx_stake.get_value(self.tx_stake.tx_hash, data)

        self.assertEqual(self.tx_stake.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_stake.address, ret_tx.address)
        self.assertEqual(self.tx_stake.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_stake.tx_type, ret_tx.tx_type)

        self.assertEqual(self.tx_stake.tx_data.stake, ret_tx.tx_data.stake)

    def test_iiss_tx_data_delegate(self):
        data: bytes = self.tx_delegate.make_value()
        ret_tx: 'IissTxData' = self.tx_delegate.get_value(self.tx_delegate.tx_hash, data)

        self.assertEqual(self.tx_delegate.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_delegate.address, ret_tx.address)
        self.assertEqual(self.tx_delegate.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_delegate.tx_type, ret_tx.tx_type)

        self.assertEqual(self.tx_delegate.tx_data.delegation_info[0].address, ret_tx.tx_data.delegation_info[0].address)
        self.assertEqual(self.tx_delegate.tx_data.delegation_info[0].ratio, ret_tx.tx_data.delegation_info[0].ratio)
        self.assertEqual(self.tx_delegate.tx_data.delegation_info[1].address, ret_tx.tx_data.delegation_info[1].address)
        self.assertEqual(self.tx_delegate.tx_data.delegation_info[1].ratio, ret_tx.tx_data.delegation_info[1].ratio)

    def test_iiss_tx_data_claim(self):
        data: bytes = self.tx_claim.make_value()
        ret_tx: 'IissTxData' = self.tx_claim.get_value(self.tx_claim.tx_hash, data)

        self.assertEqual(self.tx_claim.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_claim.address, ret_tx.address)
        self.assertEqual(self.tx_claim.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_claim.tx_type, ret_tx.tx_type)

    def test_iiss_tx_data_preb_reg_tx(self):
        data: bytes = self.tx_prep_reg.make_value()
        ret_tx: 'IissTxData' = self.tx_prep_reg.get_value(self.tx_prep_reg.tx_hash, data)

        self.assertEqual(self.tx_prep_reg.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_prep_reg.address, ret_tx.address)
        self.assertEqual(self.tx_prep_reg.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_prep_reg.tx_type, ret_tx.tx_type)

    def test_iiss_tx_data_preb_un_reg_tx(self):
        data: bytes = self.tx_prep_un_reg.make_value()
        ret_tx: 'IissTxData' = self.tx_prep_un_reg.get_value(self.tx_prep_un_reg.tx_hash, data)

        self.assertEqual(self.tx_prep_un_reg.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_prep_un_reg.address, ret_tx.address)
        self.assertEqual(self.tx_prep_un_reg.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_prep_un_reg.tx_type, ret_tx.tx_type)

    def _dump_mock_db(self):
        key: bytes = self.iiss_header.make_key()
        value: bytes = self.iiss_header.make_value()
        self.db.put(key, value)

        if self.debug:
            print("===IISS_HEADER===")
            print(f"version: {self.iiss_header.version}")
            print(f"block_height: {self.iiss_header.block_height}")
            print(f"key: {key}")
            print(f"value: {value}")
            print("")

        key: bytes = self.iiss_gv.make_key()
        value: bytes = self.iiss_gv.make_value()
        self.db.put(key, value)

        if self.debug:
            print("===IISS_GOVERNANCE_VARIABLE===")
            print(f"icx_price: {self.iiss_gv.icx_price}")
            print(f"incentive_rep: {self.iiss_gv.incentive_rep}")
            print(f"key: {key}")
            print(f"value: {value}")
            print("")

        key: bytes = self.iiss_prep.make_key()
        value: bytes = self.iiss_prep.make_value()
        self.db.put(key, value)

        if self.debug:
            print("===PREPS_DATA===")
            print(f"address: {self.iiss_prep.address}")
            print(f"block_generate_count: {self.iiss_prep.block_generate_count}")
            print(f"block_validate_count: {self.iiss_prep.block_validate_count}")
            print(f"key: {key}")
            print(f"value: {value}")
            print("")

        key: bytes = self.tx_stake.make_key()
        value: bytes = self.tx_stake.make_value()
        self.db.put(key, value)

        if self.debug:
            print("===IISS_TX_DATA-1===")
            print(f"tx_hash: {self.tx_stake.tx_hash}")
            print(f"address: {self.tx_stake.address}")
            print(f"block_height: {self.tx_stake.block_height}")
            print(f"tx_type: {self.tx_stake.tx_type}")
            print(f"stake: {self.tx_stake.tx_data.encode()}")
            print(f"key: {key}")
            print(f"value: {value}")
            print("")

        key: bytes = self.tx_delegate.make_key()
        value: bytes = self.tx_delegate.make_value()
        self.db.put(key, value)

        if self.debug:
            print("===IISS_TX_DATA-2===")
            print(f"tx_hash: {self.tx_delegate.tx_hash}")
            print(f"address: {self.tx_delegate.address}")
            print(f"block_height: {self.tx_delegate.block_height}")
            print(f"tx_type: {self.tx_delegate.tx_type}")
            print(f"ori_delegate: {[(str(x.address), x.ratio) for x in self.tx_delegate.tx_data.delegation_info]}")
            print(f"delegate: {self.tx_delegate.tx_data.encode()}")
            print(f"key: {key}")
            print(f"value: {value}")
            print("")

        key: bytes = self.tx_claim.make_key()
        value: bytes = self.tx_claim.make_value()
        self.db.put(key, value)

        if self.debug:
            print("===IISS_TX_DATA-3===")
            print(f"tx_hash: {self.tx_claim.tx_hash}")
            print(f"address: {self.tx_claim.address}")
            print(f"block_height: {self.tx_claim.block_height}")
            print(f"tx_type: {self.tx_claim.tx_type}")
            print(f"data: {self.tx_claim.tx_data.encode()}")
            print(f"key: {key}")
            print(f"value: {value}")
            print("")

        key: bytes = self.tx_prep_reg.make_key()
        value: bytes = self.tx_prep_reg.make_value()
        self.db.put(key, value)

        if self.debug:
            print("===IISS_TX_DATA-4===")
            print(f"tx_hash: {self.tx_prep_reg.tx_hash}")
            print(f"address: {self.tx_prep_reg.address}")
            print(f"block_height: {self.tx_prep_reg.block_height}")
            print(f"tx_type: {self.tx_prep_reg.tx_type}")
            print(f"data: {self.tx_prep_reg.tx_data.encode()}")
            print(f"key: {key}")
            print(f"value: {value}")
            print("")

        key: bytes = self.tx_prep_un_reg.make_key()
        value: bytes = self.tx_prep_un_reg.make_value()
        self.db.put(key, value)

        if self.debug:
            print("===IISS_TX_DATA-5===")
            print(f"tx_hash: {self.tx_prep_un_reg.tx_hash}")
            print(f"address: {self.tx_prep_un_reg.address}")
            print(f"block_height: {self.tx_prep_un_reg.block_height}")
            print(f"tx_type: {self.tx_prep_un_reg.tx_type}")
            print(f"data: {self.tx_prep_un_reg.tx_data.encode()}")
            print(f"key: {key}")
            print(f"value: {value}")
            print("")

    def _load_mock_db(self):
        key: bytes = self.iiss_header.make_key()
        value = self.db.get(key)
        ret_h: 'IissHeader' = self.iiss_header.get_value(value)

        self.assertEqual(self.iiss_header.version, ret_h.version)
        self.assertEqual(self.iiss_header.block_height, ret_h.block_height)

        key: bytes = self.iiss_gv.make_key()
        value = self.db.get(key)
        ret_gv: 'IissGovernanceVariable' = self.iiss_gv.get_value(value)

        self.assertEqual(self.iiss_gv.icx_price, ret_gv.icx_price)
        self.assertEqual(self.iiss_gv.incentive_rep, ret_gv.incentive_rep)

        key: bytes = self.iiss_prep.make_key()
        value = self.db.get(key)
        ret_p: 'PrepsData' = self.iiss_prep.get_value(self.iiss_prep.address, value)

        self.assertEqual(self.iiss_prep.block_generate_count, ret_p.block_generate_count)
        self.assertEqual(self.iiss_prep.block_validate_count, ret_p.block_validate_count)

        key: bytes = self.tx_stake.make_key()
        value = self.db.get(key)
        ret_tx: 'IissTxData' = self.tx_stake.get_value(self.tx_stake.tx_hash, value)

        self.assertEqual(self.tx_stake.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_stake.address, ret_tx.address)
        self.assertEqual(self.tx_stake.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_stake.tx_type, ret_tx.tx_type)

        self.assertEqual(self.tx_stake.tx_data.stake, ret_tx.tx_data.stake)

        key: bytes = self.tx_delegate.make_key()
        value = self.db.get(key)
        ret_tx: 'IissTxData' = self.tx_delegate.get_value(self.tx_delegate.tx_hash, value)

        self.assertEqual(self.tx_delegate.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_delegate.address, ret_tx.address)
        self.assertEqual(self.tx_delegate.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_delegate.tx_type, ret_tx.tx_type)

        self.assertEqual(self.tx_delegate.tx_data.delegation_info[0].address, ret_tx.tx_data.delegation_info[0].address)
        self.assertEqual(self.tx_delegate.tx_data.delegation_info[0].ratio, ret_tx.tx_data.delegation_info[0].ratio)
        self.assertEqual(self.tx_delegate.tx_data.delegation_info[1].address, ret_tx.tx_data.delegation_info[1].address)
        self.assertEqual(self.tx_delegate.tx_data.delegation_info[1].ratio, ret_tx.tx_data.delegation_info[1].ratio)

        key: bytes = self.tx_claim.make_key()
        value = self.db.get(key)
        ret_tx: 'IissTxData' = self.tx_claim.get_value(self.tx_claim.tx_hash, value)

        self.assertEqual(self.tx_claim.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_claim.address, ret_tx.address)
        self.assertEqual(self.tx_claim.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_claim.tx_type, ret_tx.tx_type)

        key: bytes = self.tx_prep_reg.make_key()
        value = self.db.get(key)
        ret_tx: 'IissTxData' = self.tx_prep_reg.get_value(self.tx_prep_reg.tx_hash, value)

        self.assertEqual(self.tx_prep_reg.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_prep_reg.address, ret_tx.address)
        self.assertEqual(self.tx_prep_reg.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_prep_reg.tx_type, ret_tx.tx_type)

        key: bytes = self.tx_prep_un_reg.make_key()
        value = self.db.get(key)
        ret_tx: 'IissTxData' = self.tx_prep_un_reg.get_value(self.tx_prep_un_reg.tx_hash, value)

        self.assertEqual(self.tx_prep_un_reg.tx_hash, ret_tx.tx_hash)
        self.assertEqual(self.tx_prep_un_reg.address, ret_tx.address)
        self.assertEqual(self.tx_prep_un_reg.block_height, ret_tx.block_height)
        self.assertEqual(self.tx_prep_un_reg.tx_type, ret_tx.tx_type)


if __name__ == '__main__':
    unittest.main()
