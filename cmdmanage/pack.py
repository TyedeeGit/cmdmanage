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

import json
import inspect
from abc import ABC, abstractmethod
from typing import Callable, Type, Optional


class Packable(ABC):
    """
    A packable object.
    """
    _typename = ''
    _unpacking_types: dict[str, Type['Packable']] = {}

    @abstractmethod
    def pack(self) -> dict:
        """
        Pack object into a dict.
        :return:
        """
        pass

    @classmethod
    @abstractmethod
    def unpack(cls, data: dict) -> 'Packable':
        """
        Unpack a dict into an object.
        :param data:
        """
        pass

    @classmethod
    @property
    def typename(cls):
        """
        Name of type.
        :return:
        """
        return cls._typename if cls._typename else cls.__name__.lower()

    @classmethod
    def unpacking_types(cls) -> dict[str, Type['Packable']]:
        """
        Dict containing types matching names for unpacking.
        :return:
        """
        return Packable._unpacking_types

    @classmethod
    def register_packable(cls, obj: Optional[str] | Type = None) -> Callable[[Type], Type] | Type:
        """
        Register a packable type.
        :param obj:
        :return:
        """
        if isinstance(obj, Optional[str]):
            name = obj

            def func(t: Type) -> Type:
                """
                :param t:
                :return:
                """
                typename = name if name is not None else getattr(t, 'typename', cls.__name__.lower())
                if not inspect.isabstract(t):
                    Packable._unpacking_types[typename] = t
                return t
            return func
        if isinstance(obj, Type):
            name = getattr(obj, 'typename', cls.__name__.lower())
            if not inspect.isabstract(obj):
                Packable._unpacking_types[name] = obj
            return obj

    def __init_subclass__(cls, **kwargs):
        cls.register_packable(cls)

class MyPackable(Packable):
    typename = 'some_name'

    def pack(self) -> dict:
        return {}

    @classmethod
    def unpack(cls, data: dict) -> 'MyPackable':
        return cls()

def pack(obj: Packable) -> dict:
    """
    Pack an object into a dict.
    :param obj:
    :return:
    """
    for key, value in obj.unpacking_types().items():
        if value == type(obj):
            obj_type = key
            break
    else:
        raise TypeError(f'Type "{obj.__class__.__name__}" is not a registered Packable!')
    return {'type': obj_type} | obj.pack()

def packs(obj: Packable) -> str:
    """
    Pack an object into a json string.
    :param obj:
    :return:
    """
    return json.dumps(pack(obj))

def unpack(data: dict) -> Packable:
    """
    Unpack a dict into an object.
    :param data:
    :return:
    """
    if 'type' not in data:
        raise ValueError('No type specified in data!')
    if data['type'] not in Packable.unpacking_types():
        raise ValueError(f'No registered type "{data['type']}"!')
    return Packable.unpacking_types()[data['type']].unpack(data)

def unpacks(data: str) -> Packable:
    """
    Unpack a string into an object.
    :param data:
    :return:
    """
    return unpack(json.loads(data))
