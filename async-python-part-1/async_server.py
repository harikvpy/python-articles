#!/usr/bin/env python
# async_server.py; use Python v3.9+
import asyncio


class EchoServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        peername = transport.get_extra_info('peername')
        print('Connection from {}'.format(peername))
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print('Data received: {!r}'.format(message), flush=True)

        task = asyncio.get_running_loop().create_task(self.simulate_network_io(message))  # noqa
        task.add_done_callback(self.handle_network_io_result)

    async def simulate_network_io(self, message: str):
        return await asyncio.sleep(0.1, result=message.upper())

    def handle_network_io_result(self, task):
        message = task.result()
        print('Sending back: {!r}'.format(message))
        self.transport.write(bytes(message, 'utf-8'))
        self.transport.close()


async def main():
    # Get a reference to the event loop as we plan to use low-level APIs.
    loop = asyncio.get_running_loop()

    server = await loop.create_server(
        lambda: EchoServerProtocol(),
        'localhost', 9090)

    async with server:
        await server.serve_forever()


if __name__ == "__main__":
    asyncio.run(main())
