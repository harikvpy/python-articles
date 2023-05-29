# Async Python - Part 1
<cite>Hariharan Mahadevan(何瑞理), hari@smallpearl.com</cite>

## Introduction
In the previous article on [Python Generators](http://www.google.com/) we saw how generator functions are essentially objects that represent the function, execution of which can be suspended and resumed. The resumption of the function happens when it has new values to *emit* to the caller, which it does via the *yield* statement.

In this and quite likely the next few articles we will leverage this knowhow to show how this infrastructure facilitates asynchronous programming constructs.

But before we delve into it, it makes sense to examine the origins of the need for asynchronous programming.

Asynchronous programming is not an easy concept to grasp. Quite frankly it can be frustrating at times and in my experience requires repeated attempts to get your thinking in tune with the way the paradigm works. This is because our brain is inherently trained to think sequentially connecting pieces of information together that occur in a time series to form the complete picture. Asynchronous programming does not work like that. Computing occurs asynchronously, emitting results as and when they are available in an unpredictable sequence.

There are many articles on the web that introduce asyn programming in Python and the ones I have seen mostly start with explaining the basic syntax keywords (*async* & *await*) tha enable async programming and then go deeper. While this works for most people, I feel this approach works best for those who have had some exposure to async programming concepts (Javascript, which is inherently an async language) prior.

My approach is going to be a little bit different. First I want to start with a sample code that shows the differences and the benefits of async programming. With the help of this example, we make a case for async and explain a production scenario where this can be applied.

In a subsequent lesson we will try and link the async constructs with what we learned in the Python Generators article and see how the former was adapted to implement the latter. And if necessary we'll cover the syntax, but hopefully with a different viewpoint and way to explain it.

## Example
Like I mentioned, async programming can be frustratingly difficult to understand at first. So before we go into the dry discussion of its syntax, let's start with some code. Code that you can copy-paste into an editor and run yourself.

The code below implements a TCP/IP echo server that will echo back the text written to it, but after converting it to upper case. There are two implementations, one traditional thread based server and another an async programming based single-threaded server.

### Thread based server

```
#!/usr/bin/env python
# threaded_server.py
import socketserver
import threading
import signal
import time

quit_event = threading.Event()


def quit_handler(*args):
    quit_event.set()


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        print('Connection from {}'.format(self.client_address[0]))
        print('Data received: {0}'.format(self.data))
        time.sleep(0.100)     # sleep 100 milliseconds, simulating IO
        # just send back the same data, but upper-cased
        print('Sending back: {0}'.format(self.data.upper()))
        self.request.sendall(self.data.upper())


class MyServer(threading.Thread):
    '''Start a TCP/IP server at <host>:<port>'''
    def __init__(self, host: str, port: int, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._tcp_server = socketserver.TCPServer((host, port), MyTCPHandler)

    def stop(self):
        self._tcp_server.shutdown()
        self.join()

    def run(self) -> None:
        self._tcp_server.serve_forever()


if __name__ == "__main__":
    server = MyServer('localhost', 9090)
    server.start()

    print("Press CTRL+C to stop..")
    signal.signal(signal.SIGTERM, quit_handler)     # Termination signal
    signal.signal(signal.SIGINT, quit_handler)      # CTRL+C
    quit_event.wait(None)

    print('Quitting..')
    server.stop()
    print('Done.')
```
The code above is adapted from the sample in the official doc [here](https://docs.python.org/3/library/socketserver.html#socketserver-tcpserver-example). Besides the signal handlers to instrument a graceful exit, one key change is that before returning the uppercase version of the written string, a delay of 100 milliseconds has been added. This is to simulate an IO operation. To illustrate with a real-world example, you can imagine this delay as the time required to execute a complex SQL statement or time required to run face detection algorithms in a remote server.


### Async server
```
#!/usr/bin/env python
# async_server.py; use Python v3.7+
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
```

Like *threaded_server.py*, *async_server.py* is also based on the code from the official doc [here](https://docs.python.org/3/library/asyncio-protocol.html?highlight=asyncio%20protocol#tcp-echo-server). Notable change is the delay introduced in the threaded server simulating an IO bound operation (*simulate_network_io* method of *EchoServerProtocol*). The implemtation of the server itself looks very different and there are some tricky async going on there, but we don't have to cover that now.

### Client
Now that we have two identical servers, one threaded and another implemented using async, we need to write our client. Since we're going to compare the behavior of these two servers, to make a fair comparison, we need to use the same client. Without going too much into the details, here is the code.

```
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
```
The client takes three arguments, two of which are required. These are address of the server and its port. The last argument is the number of requests to make to the server during the test, which defaults to 100.

It's not hard to notice that the client code uses asyncio. Why? This implementation detail merits a brief explanation.

To stress the server we need make as many simultaneous connections to the server as possible. Only this would simulate a real-life server where client connections come from different machines all connected to the network. One way to simulate this would be to spawn *n* number of threads. But on a personal computer, with limited CPU cores, spawning 1000 threads will place excessive load on its resources, which in turn would affect our server (remember the server is also running on the same machine). To get around this, we employ async programming. We don't have to go deeper than this at the moment. As we progress with our discussion, the reasons for this will become clearer.

### Run the code
Assuming that you have the three files saved, you can run it like this.

From Terminal 1:
```
$ python threaded_server.py
```
From Terminal 2:
```
$ python ./client.py localhost 9090 1000
```

Note the time it takes to process 1000 requests. Now do the same with the async server.

From Terminal 1:
```
$ python async_server.py
```
And from Terminal 2:
```
$ python ./client.py localhost 9090 1000
```

You will observe that the time it takes to process the 1000 echo requests is significantly lower for the async server when compared to the threaded counterpart.

#### NOTE
If you want to get funky and get scientific with the actual execution times, you may use Python's builtin profiler like this:

```
$ python -m cProfile ./client.py localhost 9090 1000 | grep 'function calls'
88617 function calls (88004 primitive calls) in 0.331 seconds
```

Piping the output to grep is to filter out the noise of profiler's individual function call timing details, which is not relevant for our experiment. 

## Discussion

In programming language theory, functions that can capture their state (both code & data) and suspend & resume themselves, are generally referred to as a closure, origins of which can be traced back to the 1970s (and even earlier, *lambda calculus*). However, closures have become particularly popular in the recent years where computing has become IO intensive. IO intensive programs spend more of their computing resources waiting for IO requests to return with their reply than exercising the CPU doing heavy computation. IO could involve waiting for network requests, executing database queries, sending tasks to task queues, etc.

In all of the above scenarios, one of the more popular programming models has been of a server program serving multiple simultaneous clients structured around threads as a means for separating context. That is, as new client requests come in, a different thread is assigned to it and CPU's thread scheduling mechanism takes care of its scheduling. Unfortunately, for many programs this has turned out to be bit of an overkill. This is because, threads, while magically allowing multiple programs to seemingly run concurrently, are also expensive when they need to be switched in & out of the processor.

Experts figured out that many computing tasks hardly involve any physical computation requiring substantial CPU cycles and are primarily concerned with supplying with results read from other tasks or from files. And when a computation involves CPU cycles, often the results can be cached so that further requests for the same computation can be supplied with the results of the previous computation. Such tasks tend to spend more of their time waiting for the IO requests to complete before they can return the results back to the caller.

Why not capture the results of these 

