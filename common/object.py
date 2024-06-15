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
from abc import ABC, abstractmethod
from typing import Self
from .exceptions import ObjectError

class Object(ABC):
    obj_type = 'object'

    def __init__(self):
        """
        Contains information about an object. Can be converted to and from dictionaries.
        """
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert an object to a dictionary.
        :return:
        """
        return {'type': self.obj_type}

    @classmethod
    @abstractmethod
    def from_dict(cls, data: dict) -> Self:
        """
        Convert a dictionary to an object.
        :param data:
        :return:
        """
        if data.get('type', '') != cls.obj_type:
            raise ObjectError(f"Expected object of type '{cls.obj_type}', got '{data.get('type', '')}'")
