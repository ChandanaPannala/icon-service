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

from iconservice.database.db import KeyValueDatabase


class IissDatabase(KeyValueDatabase):
    def __init__(self, db: plyvel.DB) -> None:
        super().__init__(db)

    # todo: consider more good method name
    def reset_db(self, path, create_if_missing=True):
        self._db = plyvel.DB(path, create_if_missing=create_if_missing)

