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

from ...icx.icx_storage import IcxStorage
from ..database.iiss_batch import IissBatchManager
from ..iiss_data_storage import IissDataStorage
from ..reward_calc_proxy import RewardCalcProxy


class PrepDelegator:
    icx_storage: 'IcxStorage' = None
    batch_manager: 'IissBatchManager' = None
    data_storage: 'IissDataStorage' = None
    reward_calc_proxy: 'RewardCalcProxy' = None
    global_variable: 'IissGlobalVariable' = None