"""
Copyright (c) 2024 Tyedee

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import pickle
import socket
import struct
from typing import Optional

class PipeError(IOError):
    pass

class SocketPipe:
    def __init__(self, address: tuple[str, int]):
        """
        A socket with automatic pickling and unpickling.
        """
        self.sock: Optional[socket.socket] = None
        self.conn: Optional[socket.socket] = None
        self.connected = False
        self.address = address

    def send(self, obj: object, handle_exception=True) -> bool:
        """
        Send a picklable object.
        :param handle_exception:
        :param obj:
        :return:
        """
        if not self.connected:
            raise PipeError('Pipe is not connected!')
        try:
            data = pickle.dumps(obj)
            length = struct.pack('!I', len(data))
            self.conn.sendall(length)
            self.conn.sendall(data)
            return True
        except OSError as e:
            if handle_exception:
                return False
            raise e

    def recv(self, handle_exception=True) -> object:
        """
        Receive a picklable object.
        :return:
        """
        if not self.connected:
            raise PipeError('Pipe is not connected!')
        try:
            length_data = self._recv(4)
            if not length_data:
                return None
            length = struct.unpack('!I', length_data)[0]
            data = self._recv(length)
            obj = pickle.loads(data)
            return obj
        except OSError as e:
            if handle_exception:
                return None
            raise e

    def _recv(self, length: int) -> bytes:
        """
        Helper function to receive the specified amount of data
        :param length:
        :return:
        """
        if not self.connected:
            raise PipeError('Pipe is not connected!')
        data = b''
        while len(data) < length:
            more = self.conn.recv(length - len(data))
            if not more:
                raise EOFError('Socket closed before receiving all data')
            data += more
        return data

    def close(self):
        """
        Close the socket.
        :return:
        """
        if self.connected:
            self.conn.close()
        self.connected = False

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

class ClientSocketPipe(SocketPipe):
    def __init__(self, address: tuple[str, int]):
        """
        A socketpipe client.
        :param address:
        """
        super().__init__(address)

    def connect(self):
        """
        Connect to a socketpipe server.
        :return:
        """
        self.conn = socket.socket(type=socket.SOCK_STREAM)
        self.conn.connect(self.address)
        self.connected = True

class ServerSocketPipe(SocketPipe):
    def __init__(self, address=('127.0.0.1', 0)):
        """
        A socketpipe server.
        :param address:
        """
        super().__init__(address)
        self.sock = socket.socket(type=socket.SOCK_STREAM)
        self.sock.bind(self.address)
        self.address = self.sock.getsockname()
        self.sock.listen(1)


    def get_client(self) -> ClientSocketPipe:
        """
        Create a client end of the socketpipe.
        :return:
        """
        return ClientSocketPipe(self.address)

    def accept(self):
        """
        Accept a connection to a client socket.
        :return:
        """
        self.conn, _ = self.sock.accept()
        self.connected = True

    def __exit__(self, exc_type, exc_val, exc_tb):
        super().__exit__(exc_type, exc_val, exc_tb)
        self.sock.close()

def new_socketpipe():
    sock = ServerSocketPipe()
    return sock, sock.get_client()