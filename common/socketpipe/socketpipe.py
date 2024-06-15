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
from abc import ABC, abstractmethod

class PipeError(IOError):
    pass

class Pipe(ABC):
    @abstractmethod
    def send(self, obj: object, handle_exception=True) -> bool:
        """
        Send a picklable object.
        :param obj:
        :param handle_exception:
        :return:
        """
        pass

    @abstractmethod
    def recv(self, handle_exception=True) -> object:
        """
        Receive a picklable object.
        :return:
        """
        pass

    @abstractmethod
    def recv_all(self, length: int) -> bytes:
        """
        Receive exactly a specified amount of bytes.
        :param length:
        :return:
        """
        pass

    @abstractmethod
    def recv_bytes(self, amount: int) -> bytes:
        """
        Receive up to a specified amount of bytes.
        :param amount:
        :return:
        """
        pass

    @abstractmethod
    def send_bytes(self, data: bytes):
        """
        Send bytes.
        :param data:
        :return:
        """
        pass

    @abstractmethod
    def close(self):
        """
        Close the pipe.
        :return:
        """
        pass

class SocketPipe(Pipe):
    def __init__(self, address: tuple[str, int]):
        """
        A socket with automatic pickling and unpickling that can act as a pipe.
        """
        self.sock: Optional[socket.socket] = None
        self.conn: Optional[socket.socket] = None
        self.connected = False
        self.address = address

    def send(self, obj: object, handle_exception=True) -> bool:
        if not self.connected:
            raise PipeError('Pipe is not connected!')
        try:
            data = pickle.dumps(obj)
            length = struct.pack('!I', len(data))
            self.send_bytes(length)
            self.send_bytes(data)
            return True
        except OSError as e:
            if handle_exception:
                return False
            raise e

    def recv(self, handle_exception=True) -> object:
        if not self.connected:
            raise PipeError('Pipe is not connected!')
        try:
            length_data = self.recv_bytes(4)
            if not length_data:
                return None
            length = struct.unpack('!I', length_data)[0]
            data = self.recv_bytes(length)
            obj = pickle.loads(data)
            return obj
        except OSError as e:
            if handle_exception:
                return None
            raise e

    def recv_all(self, length: int) -> bytes:
        if not self.connected:
            raise PipeError('Pipe is not connected!')
        data = b''
        while len(data) < length:
            more = self.recv_bytes(length - len(data))
            if not more:
                raise EOFError('Socket closed before receiving all data')
            data += more
        return data

    def send_bytes(self, data: bytes):
        if not self.connected:
            raise PipeError('Pipe is not connected!')
        self.conn.sendall(data)

    def recv_bytes(self, amount: int) -> bytes:
        if not self.connected:
            raise PipeError('Pipe is not connected!')
        return self.conn.recv(amount)

    def close(self):
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