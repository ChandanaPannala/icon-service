#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright 2018 ICON Foundation
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

from iconservice.base.exception import InvalidParamsException
from iconservice.icon_constant import REVISION_4, REVISION_3
from iconservice.icx.icx_account import AccountType, Account, Delegations
from tests import create_address


class TestAccountType(unittest.TestCase):
    def test_account_type(self):
        self.assertTrue(AccountType.GENERAL == 0)
        self.assertTrue(AccountType.GENESIS == 1)
        self.assertTrue(AccountType.TREASURY == 2)

        self.assertTrue(str(AccountType.GENERAL) == 'GENERAL')
        self.assertTrue(str(AccountType.GENESIS) == 'GENESIS')
        self.assertTrue(str(AccountType.TREASURY) == 'TREASURY')

    def test_from_int(self):
        self.assertEqual(AccountType.GENERAL, AccountType.from_int(0))
        self.assertEqual(AccountType.GENESIS, AccountType.from_int(1))
        self.assertEqual(AccountType.TREASURY, AccountType.from_int(2))

        self.assertRaises(ValueError, AccountType.from_int, 3)


class TestAccount(unittest.TestCase):
    def test_account_revision_3(self):
        account1 = Account()
        self.assertIsNotNone(account1)
        self.assertIsNone(account1.address)
        self.assertTrue(account1.balance == 0)
        account1.address = create_address()

        account1.deposit(100)
        self.assertEqual(100, account1.balance)

        account1.withdraw(100)
        self.assertEqual(0, account1.balance)

        # wrong value
        self.assertRaises(InvalidParamsException, account1.deposit, -10)

        # 0 transfer is possible
        old = account1.balance
        account1.deposit(0)
        self.assertEqual(old, account1.balance)

        self.assertRaises(InvalidParamsException, account1.withdraw, -11234)
        self.assertRaises(InvalidParamsException, account1.withdraw, 1)

        old = account1.balance
        account1.withdraw(0)
        self.assertEqual(old, account1.balance)

    def test_account_from_bytes_to_bytes_revision_3(self):
        account = Account()

        data = account.to_bytes()
        self.assertTrue(isinstance(data, bytes))
        self.assertEqual(36, len(data))

        account2 = Account.from_bytes(data)
        self.assertFalse(account2.locked)
        self.assertEqual(AccountType.GENERAL, account2.type)
        self.assertEqual(0, account2.balance)

        account.type = AccountType.GENESIS
        account.deposit(1024)

        account3 = Account.from_bytes(account.to_bytes())
        self.assertEqual(AccountType.GENESIS, account3.type)
        self.assertEqual(1024, account3.balance)

    def test_account_from_bytes_to_bytes_revision_4(self):
        account = Account()

        data = account.to_bytes(REVISION_4)
        self.assertTrue(isinstance(data, bytes))
        self.assertEqual(14, len(data))

        account2 = Account.from_bytes(data)
        self.assertFalse(account2.locked)
        self.assertEqual(AccountType.GENERAL, account2.type)
        self.assertEqual(0, account2.balance)

        account.type = AccountType.GENESIS
        account.deposit(1024)

        account3 = Account.from_bytes(account.to_bytes(REVISION_4))
        self.assertEqual(AccountType.GENESIS, account3.type)
        self.assertEqual(1024, account3.balance)

        account.iiss.stake = 10 ** 20
        account.iiss.delegated_amount = 100000

        d = Delegations()
        d.address = create_address()
        d.value = 10 ** 30
        account.iiss.delegations.append(d)
        account.iiss.delegations.append(d)
        account4 = Account.from_bytes(account.to_bytes(REVISION_4))

        self.assertEqual(account, account4)

    def test_account_from_bytes_to_bytes_old_db_load_revision_4(self):
        account = Account()

        balance = 1024
        account.type = AccountType.GENERAL
        account.deposit(balance)

        account1 = Account.from_bytes(account.to_bytes(REVISION_3))
        self.assertEqual(account, account1)

        data: bytes = account.to_bytes(REVISION_4)
        account2 = Account.from_bytes(data)
        self.assertEqual(account, account2)


if __name__ == '__main__':
    unittest.main()
