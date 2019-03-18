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

from shutil import rmtree
from typing import TYPE_CHECKING

import plyvel
import unittest

from iconservice.iiss.prep.prep_candidate import PrepCandidateRegInfo, GovernanceVariables
from tests import create_address

if TYPE_CHECKING:
    from iconservice.base.address import Address


class TestPrepCandidateRegInfo(unittest.TestCase):
    db_path: str = './mock_db'

    def setUp(self):
        self.db = plyvel.DB('./mock_db', create_if_missing=True)
        self.debug = False

        self.prep_reg_info: 'PrepCandidateRegInfo' = PrepCandidateRegInfo()
        self.prep_reg_info.address: 'Address' = create_address()
        self.prep_reg_info.network_info: str = "192.168.0.1"
        self.prep_reg_info.name: str = "mycom22"
        self.prep_reg_info.url: str = "https://icon.foundation/?lang=en"
        self.prep_reg_info.block_height: int = 12345
        gv: "GovernanceVariables" = GovernanceVariables()
        gv.icxPrice: int = 10 * 100
        gv.incentiveRep: int = 10 * 1000
        self.prep_reg_info.gv: 'GovernanceVariables' = gv

    def tearDown(self):
        rmtree(self.db_path)
        pass

    def test_iiss_data_using_level_db(self):
        self._dump_mock_db()
        self._load_mock_db()

    def test_iiss_header_data(self):
        addr: 'Address' = self.prep_reg_info.address
        data: bytes = self.prep_reg_info.to_bytes()
        ret_p: 'PrepCandidateRegInfo' = self.prep_reg_info.from_bytes(addr, data)

        self.assertEqual(self.prep_reg_info.address, ret_p.address)
        self.assertEqual(self.prep_reg_info.network_info, ret_p.network_info)
        self.assertEqual(self.prep_reg_info.name, ret_p.name)
        self.assertEqual(self.prep_reg_info.url, ret_p.url)
        self.assertEqual(self.prep_reg_info.block_height, ret_p.block_height)

        self.assertEqual(self.prep_reg_info.gv.icxPrice, ret_p.gv.icxPrice)
        self.assertEqual(self.prep_reg_info.gv.incentiveRep, ret_p.gv.incentiveRep)

    def _dump_mock_db(self):
        key: bytes = self.prep_reg_info.make_key()
        value: bytes = self.prep_reg_info.to_bytes()
        self.db.put(key, value)

    def _load_mock_db(self):
        key: bytes = self.prep_reg_info.make_key()
        value = self.db.get(key)
        ret_p: 'PrepCandidateRegInfo' = self.prep_reg_info.from_bytes(self.prep_reg_info.address, value)

        self.assertEqual(self.prep_reg_info.address, ret_p.address)
        self.assertEqual(self.prep_reg_info.network_info, ret_p.network_info)
        self.assertEqual(self.prep_reg_info.name, ret_p.name)
        self.assertEqual(self.prep_reg_info.url, ret_p.url)
        self.assertEqual(self.prep_reg_info.block_height, ret_p.block_height)

        self.assertEqual(self.prep_reg_info.gv.icxPrice, ret_p.gv.icxPrice)
        self.assertEqual(self.prep_reg_info.gv.incentiveRep, ret_p.gv.incentiveRep)


if __name__ == '__main__':
    unittest.main()
