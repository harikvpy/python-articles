#!/usr/bin/env python
# client.py; use Python 3.9+
from typing import Tuple, Any
import asyncio
import sys


class EchoClientProtocol(asyncio.Protocol):
    def __init__(self, message, on_con_lost):
        self.message = message
        self.on_con_lost = on_con_lost

    def connection_made(self, transport):
        transport.write(self.message.encode())
        print('Data sent: {!r}'.format(self.message))

    def data_received(self, data):
        print('Data received: {!r}'.format(data.decode()))

    def connection_lost(self, exc):
        # print('The server closed the connection')
        self.on_con_lost.set_result(True)


async def client(address: str, port: int) -> Tuple[asyncio.Transport, asyncio.Future[Any]]:     # noqa
    # Get a reference to the event loop as we plan to use
    # low-level APIs.
    loop = asyncio.get_running_loop()

    on_con_lost = loop.create_future()

    MESSAGE = 'the quick brown fox jumps over the lazy dog'
    transport, protocol = await loop.create_connection(
        lambda: EchoClientProtocol(MESSAGE, on_con_lost),
        address, port)

    return (transport, on_con_lost)


async def run_clients(count: int, address: str, port: int):
    transports = []
    futures = []
    for i in range(0, count):
        transport, con_lost_future = await client(address, port)
        transports.append(transport)
        futures.append(con_lost_future)

    # Wait until all the client connections are closed
    # Then close all the transports created.
    try:
        await asyncio.gather(*futures)
    finally:
        # close all transports
        for t in transports:
            t.close()


if __name__ == "__main__":
    iter = 100
    if len(sys.argv) < 3:
        print("Usage: client <address> <port> [<iterations>]\n")
        sys.exit(1)
    else:
        address = sys.argv[1]
        port = sys.argv[2]
    if len(sys.argv) > 3:
        iter = int(sys.argv[3])
    print(f"Creating {iter} connections to echo server at {address}:{port}...")
    asyncio.run(run_clients(iter, address, port))
