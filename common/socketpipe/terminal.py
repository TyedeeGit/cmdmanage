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
import sys
import pickle
from subprocess import Popen, CREATE_NEW_CONSOLE, TimeoutExpired
from typing import Optional, Self, Callable
from .socketpipe import new_socketpipe

class TerminalError(Exception):
    pass

class Terminal:
    def __init__(self, target: Optional[Callable] = None, args=()):
        """
        A terminal host interface.
        """
        self.proc: Optional[Popen] = None
        self.target = target
        self.args = args

    def start(self) -> Self:
        """
        Start the terminal process.
        :return:
        """
        host_pipe, proc_pipe = new_socketpipe()
        with host_pipe:
            code = f"""
import pickle
import sys
import traceback


class Debugger:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            print(traceback.format_exc().rstrip(), file=sys.stderr)
            input()
        return True


def get_pipe():
    pipe = pickle.loads({pickle.dumps(proc_pipe)!r})
    pipe.connect()
    return pipe


def run():
    with Debugger():
        with get_pipe() as proc_pipe:
            try:
                target = pickle.loads({pickle.dumps(self.target)!r})
                args = pickle.loads({pickle.dumps(self.args)!r})
            except Exception as e:
                proc_pipe.send(e)
            else:
                proc_pipe.send(None)
                target(*args)


if __name__ == "__main__":
    run()
        """
            self.proc = Popen([sys.executable, '-c', code], creationflags=CREATE_NEW_CONSOLE)
            host_pipe.accept()
            e = host_pipe.recv()
            if e is not None:
                raise e
        return self

    def wait(self, timeout: Optional[float] = None) -> int:
        """
        Wait for terminal process to terminate
        :param timeout:
        :return:
        """
        try:
            return self.proc.wait(timeout=timeout)
        except TimeoutExpired:
            return None

    def close(self):
        """
        Close the terminal.
        :return:
        """
        if self.proc is not None:
            self.proc.terminate()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_val is not None:
            raise TerminalError('An exception occurred inside the terminal object.')
