# Async Python - Part 1
<cite>Hariharan Mahadevan(何瑞理), hari@smallpearl.com</cite>

## Introduction
In the previous article on [Python Generators](https://lsl.sinica.edu.tw/Blog/2023/05/python-generators-a-look-inside/) we saw how generator functions are essentially objects that represent the function, execution of which can be suspended and resumed. The resumption of the function happens when it has new values to *emit* to the caller, which it does via the *yield* statement. With this background knowledge, in this (and quite likely a few) article we will start examining asynchronous programming in python.

Asynchronous programming is not an easy concept to grasp. Quite frankly it can be frustrating at times and in my experience, it is one of those subjects that requires repeated attempts to get your thinking in tune with the way the paradigm works. This is because our brain is inherently trained to think sequentially connecting information that occurs in a time series to form the complete picture. Asynchronous programming does not work like that. Computing occurs asynchronously, emitting results as and when they are available in an unpredictable sequence.

There are many articles on the web that introduce async programming in Python and the ones I have seen mostly start with explaining the basic syntax keywords (*async* & *await*) tha enable async programming and then go deeper. While this works for most people, I feel this approach works best for those who have had some exposure to async programming concepts (Javascript, which is inherently an async language) prior.

My approach is going to be a little bit different. First I want to start with a sample code that shows the differences & benefits of async programming proving what it can result in compared with the more conventional paradigms of concurrency. Once we make the case for async, we can move on to explain a production scenario where this can be applied.

In a subsequent lesson we will link the async constructs with what we learned in the Python Generators article and see how the former was adapted to implement the latter. And if necessary we'll cover the syntax, but hopefully with a different viewpoint than the many articles already existing on the web.

## Example
The code below implements a TCP/IP echo server that will echo back the text written to it, but after converting it to upper case. There are two implementations, one traditional thread based server and another an async programming based single-threaded server.

Then we implement a client that will exercise this echo server. Since the server implementation is opaque to the client, we can run the client on the two server implentations and observe & compare the results.

### Thread based server

```python showLineNumbers
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
        # DB request
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

The code above is adapted from the sample in the official doc [here](https://docs.python.org/3/library/socketserver.html#socketserver-tcpserver-example). Besides the signal handlers to instrument a graceful exit, one key change is that before returning the uppercase version of the written string to the client, there is a delay of 100 milliseconds. This is to simulate an IO operation. To illustrate with a real-world example, you can imagine this delay as the time required to execute a complex SQL statement or time required to run face detection algorithms in a remote server.


### Async server
```python showLineNumbers
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
        # DB request
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

Like *threaded_server.py*, *async_server.py* is also based on the code from the official doc [here](https://docs.python.org/3/library/asyncio-protocol.html?highlight=asyncio%20protocol#tcp-echo-server). Notable change is the delay introduced simulating an IO bound operation (*simulate_network_io* method of *EchoServerProtocol*). The implemtation of the server looks very different from the threaded server, but this understandable as we're using async programming for it. Also there are couple of tricky async stuff going on there, but we don't have to cover that now.

### Client
Now that we have two identical servers, one threaded and another async, we need to write our client. Since we're going to compare the behavior of these two servers, to make a fair comparison, we need to use the same client. Without going too much into the details, here is the code.

```python showLineNumbers
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

The client takes three arguments, two of which are required. These are address of the server and its port. The last argument is the number of requests to make to the server during the test, which defaults to 10000, if omitted.

### Execution results
Assuming that you have the three files saved, you can run it like this.

From Terminal 1:
```
$ python threaded_server.py
```
From Terminal 2:
```
$ python ./client.py localhost 9090 10000
```

Note the time it takes to process 10000 requests. Now do the same with the async server.

From Terminal 1:
```
$ python async_server.py
```
And from Terminal 2:
```
$ python ./client.py localhost 9090 10000
```

On my MacBook Pro i7 4870HQ (4 cores/8 hyperthreads), I get the following results.

1000 iterations:

| Server type      | Time           |
|------------------|----------------|
| Threaded server  |  1.891 seconds |
| Async server     |  1.812 seconds |

10000 iterations:

| Server type      | Time           |
|------------------|----------------|
| Threaded server  | 36.851 seconds |
| Async server     | 20.066 seconds |

As you can see as the number of iterations is increases, async server is able to scale up much better than the threaded version.


#### NOTE
The timings above were generated by profiling the code with *cProfile*, Python's builtin profiler. The commandline for this looks like this:

```
$ python -m cProfile ./client.py localhost 9090 100000 | grep 'function calls'
103731 function calls (88004 primitive calls) in 20.066 seconds
```

Piping the output to grep is to filter out the noise of profiler's individual function call timing details, which is not relevant for our experiment.

## Discussion
A server program typically is designed to serve multiple clients. Each client could make a different request with possibly different parameters. This requires that the server separate the serving context of each request so that it can isolate the client's request. One of the simplest ways of isolating execution context is to use processor threads which inherently provides this capability.

However, when serving the request involves operations that are IO intensive, the thread is essentially blocked, waiting for the IO operation to complete. When the thread is blocked waiting for an IO to complete, if other requests come in, server program would spawn another thread to serve the new request. (Of course, no server would allow infinite number of requests and often there would be an upper limit on the number of concurrent threads that it'll spawn. But let's leave that aside). And as more and more threads are created, the OS scheduler has to spend more time managing the context of the threads which itself starts to eat up more and more CPU cycles. That is scheduler (which is also a thread) starts hogging the CPU.

In the case of the async server, there's only one thread that's serving all the client requests that are coming in. This thread is the one with an active *event loop*. Don't get overawed by the terminology -- think of an *event loop* as a *do-while-true* loop that takes an input queue (conceptual queue) of tasks and executes them one by one. As an when any of these tasks have completed their previous operation, they *yield* a result back to their caller. When this happens the loop moves on to the next ask in the queue. And if there are no more tasks, it just waits until new tasks are added to queue or is asked to stop waiting, whichever happens first.

We can apply the above concept to explain our example above. As each request comes in, a request to the database server is made via *asyncio.get_running_loop().create_task(self.simulate_network_io(message)*. As the API name suggests, this creates a new task and puts it in the queue, which executes it immediately. However the code for *simulate_network_io*, consists of a *sleep*. Event loop, while executing this, gains control back and moves on to the next task while the just executed *simulate_network_io* is within it's sleep interval. When the *sleep* interval is exhausted the task is once again given attention in the loop (look keeps track of all its scheduled tasks), and this time the loop checks & notices that we have added a completion routine to the task and therefore invokes it. While at it, it also notices that the *sleep* returned a result to the task, which is used to write the response back to the client. You can refer to documentation of [sleep](https://docs.python.org/3/library/asyncio-task.html#sleeping) here for details.

The last two paragraphs is essentially the crux of asynchronous programming. You can visualize it as a conceptual queue of tasks with one person (the *loop*) assigned to take each one out of the top of it and attend to it. The tasks themselves tell the loop which of its operations could take a long time to complete. When the loop encounters these operations, it starts the operation and and puts the task back in the queue. This process repeats until the person is asked to stop serving the task queue.

## Real-world analogy
We can use a real-world analogy to explain this. Imagine being at home and doing the following:

```
------------------- time ----------------------->
Start the washing machine with dirty clothes
    Put kettle on the stove for tea
        Put two slices of bread in the toaster
            Kettle siren goes off
            Make tea
                Toaster goes pop
                Spread peanut butter on the toast and have it with tea
                    Washing machine goes 'beep beep'
                        Hang the clothes and while sipping tea and having your toast.
```
This is essentially what happens in async. You're doing many things concurrently and *seemingly* parallelly.

## Client
An observant reader might have noticed that the client code uses asyncio. Why? This implementation detail merits a brief explanation.

To stress the server we need to make as many simultaneous connections to the server as possible. Only this would simulate a real-life server where client connections come from different machines all connected to the network. One way to simulate this would be to spawn *n* number of threads. But on a personal computer, with limited CPU cores, spawning thousands of threads will place excessive load on the OS scheduler, which in turn would affect our threaded server (remember the server is also running on the same machine). To get around this, we employ async programming, making the client code the same for both tests. We don't have to go deeper than this at the moment. As we progress with our discussion, the reasons for this will become clearer.

## Wrapping up
To facilitate the async features, what one needs is a function whose state can be suspended and resumed. That means functions whose state (code & data) can be frozen so that it can be resumed later. This is exactly what generator functions provide. The only difference being that in generator functions, control is transferred back to the function via a call to the *next(fn)* iterator function. In async, the async function suspends itself when another async function is called with (via *await*) and control is transferred back to it when the awaited function is complete. And if the *await* is for a network operation, the event loop thread can make itself available for next async routine (via *await*) while the IO is in progress. This capability is what allows our example code to schedule 1000s of async routines in one event loop.

Hope this gives you a gentle introduction to asynchronous programming and some of its benefits. Bear in mind that asyncio is not a solution to everything that is wrong with multithreaded approach. The benefit comes at a cost -- code complexity. Debugging async code is hard as you would have to primarily resort to log messages to identify and troubleshoot any issues. A threaded program, on the other hand, allows you to break its execution, freezing all threads and step through the code using a traditional debugger.

If you have questions or comments, feel free to post them to the [FB page](https://www.facebook.com/AcademiaSinicaLSL) where a link to this article is posted. I'll try to check them daily and answer any questions you may have.

*<small>Hariharan is a software developer turned entrepreneur running his own software business in Taiwan. He has over 30 years of hands-on development experience in domains ranging from device drivers to cloud based applications and still enjoys coding.</small>*
