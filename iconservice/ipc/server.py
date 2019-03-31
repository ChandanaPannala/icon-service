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

import asyncio


class IPCServer(object):
    def __init__(self):
        self._loop = None
        self.server_task = None
        self._server_coroutine = None

    def open(self, loop, on_accepted, path: str):
        assert loop
        assert on_accepted
        assert isinstance(path, str)

        self._loop = loop

        coroutine = asyncio.start_unix_server(on_accepted, path)
        print(f"server_coroutine: {coroutine}")

        return coroutine

    def start(self):
        pass

    def stop(self):
        pass

    def close(self):
        if self.server_task:
            self.server_task.cancel()
            self.server_task = None
            self._server_coroutine = None

        self._loop = None
