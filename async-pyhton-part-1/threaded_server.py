#!/usr/bin/env python
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
