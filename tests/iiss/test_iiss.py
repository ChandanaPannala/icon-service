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

import unittest
from typing import TYPE_CHECKING

from iconservice.iiss.iiss_msg_data import IissHeader, IissGovernanceVariable, PrepsData, IissTxData, IissTxType, StakeTx, \
    DelegationTx, DelegationInfo, ClaimTx, PRepRegisterTx, PRepUnregisterTx
from tests import create_address

if TYPE_CHECKING:
    from iconservice.base.address import Address


class TestIissData(unittest.TestCase):
    def test_iiss_header(self):
        h = IissHeader()
        h.version = 10
        h.block_height = 10 ** 6

        data: bytes = h.make_value()
        ret_h: 'IissHeader' = h.get_value(data)

        self.assertEqual(h.version, ret_h.version)
        self.assertEqual(h.block_height, ret_h.block_height)

    def test_iiss_governance_variable(self):
        gv = IissGovernanceVariable()
        gv.icx_price = 10 ** 18
        gv.incentive_rep = 10 ** 6

        data: bytes = gv.make_value()
        ret_gv: 'IissGovernanceVariable' = gv.get_value(data)

        self.assertEqual(gv.icx_price, ret_gv.icx_price)
        self.assertEqual(gv.incentive_rep, ret_gv.incentive_rep)

    def test_preps_data(self):
        p = PrepsData()
        p.address = create_address()
        p.block_generate_count = 3
        p.block_validate_count = 10

        data: bytes = p.make_value()
        ret_p: 'PrepsData' = p.get_value(p.address, data)

        self.assertEqual(p.block_generate_count, ret_p.block_generate_count)
        self.assertEqual(p.block_validate_count, ret_p.block_validate_count)

    def test_iiss_tx_data_stake(self):
        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash'
        tx.address: 'Address' = create_address()
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.STAKE
        tx.tx_data: 'StakeTx' = StakeTx()
        tx.tx_data.stake: int = 10 ** 18

        data: bytes = tx.make_value()
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, data)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)

        self.assertEqual(tx.tx_data.stake, ret_tx.tx_data.stake)

    def test_iiss_tx_data_delegate(self):
        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash'
        tx.address: 'Address' = create_address()
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.DELEGATION
        tx.tx_data: 'DelegationTx' = DelegationTx()
        tx.tx_data.delegation_info = DelegationInfo()
        tx.tx_data.delegation_info.address_list.append(create_address())
        tx.tx_data.delegation_info.ratio_list.append(10)
        tx.tx_data.delegation_info.address_list.append(create_address())
        tx.tx_data.delegation_info.ratio_list.append(20)

        data: bytes = tx.make_value()
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, data)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)

        self.assertEqual(tx.tx_data.delegation_info.address_list[0], ret_tx.tx_data.delegation_info.address_list[0])
        self.assertEqual(tx.tx_data.delegation_info.address_list[1], ret_tx.tx_data.delegation_info.address_list[1])
        self.assertEqual(tx.tx_data.delegation_info.ratio_list[0], ret_tx.tx_data.delegation_info.ratio_list[0])
        self.assertEqual(tx.tx_data.delegation_info.ratio_list[1], ret_tx.tx_data.delegation_info.ratio_list[1])

    def test_iiss_tx_data_claim(self):
        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash'
        tx.address: 'Address' = create_address()
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.CLAIM
        tx.tx_data: 'ClaimTx' = ClaimTx()

        data: bytes = tx.make_value()
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, data)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)

    def test_iiss_tx_data_preb_reg_tx(self):
        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash'
        tx.address: 'Address' = create_address()
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.PREP_REGISTER
        tx.tx_data: 'PRepRegisterTx' = PRepRegisterTx()

        data: bytes = tx.make_value()
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, data)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)

    def test_iiss_tx_data_preb_un_reg_tx(self):
        tx = IissTxData()
        tx.tx_hash: bytes = b'tx_hash'
        tx.address: 'Address' = create_address()
        tx.block_height: int = 10 ** 3
        tx.tx_type: 'IissTxType' = IissTxType.PREP_REGISTER
        tx.tx_data: 'PRepUnregisterTx' = PRepUnregisterTx()

        data: bytes = tx.make_value()
        ret_tx: 'IissTxData' = tx.get_value(tx.tx_hash, data)

        self.assertEqual(tx.tx_hash, ret_tx.tx_hash)
        self.assertEqual(tx.address, ret_tx.address)
        self.assertEqual(tx.block_height, ret_tx.block_height)
        self.assertEqual(tx.tx_type, ret_tx.tx_type)


if __name__ == '__main__':
    unittest.main()
