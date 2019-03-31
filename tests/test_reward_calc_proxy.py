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
from asyncio import StreamReader, StreamWriter

from iconservice.ipc.server import IPCServer


async def on_echo(reader: StreamReader, writer: StreamWriter):
    print('on_echo() start')

    while True:
        data = await reader.read(1024)
        if len(data) == 0:
            break

        print(f'client -> server: {data.decode()}({len(data)})')

        if data == b'stop':
            break
        elif data == b'loopstop':
            loop = asyncio.get_running_loop()
            loop.stop()
            break

        writer.write(data)
        await writer.drain()

    writer.close()

    print('on_echo() end')


async def on_accepted(reader, writer):
    print('on_accepted() start')
    asyncio.create_task(on_echo(reader, writer))
    print('on_accepted() end')


async def main():
    print("main() start")

    loop = asyncio.get_running_loop()
    print(f"loop: {loop}")

    server = IPCServer()
    server_task = await server.open(loop, on_accepted, "/tmp/is.sock")
    print(f"server_task: {server_task}")

    try:
        await server_task.serve_forever()
    except Exception as e:
        print(e)
    finally:
        server.close()

    print("main() end")


if __name__ == '__main__':
    asyncio.run(main(), debug=True)
