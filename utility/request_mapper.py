from flask import request, jsonify
from functools import wraps
import datetime
from typing import get_type_hints, List
from collections import namedtuple
import decimal
import os, socket

def request_json_mapping(class_):
    """This decorator takes the class/namedtuple to convert any JSON data in incoming request."""
    def wrapper(func):
        @wraps(func)
        def decorator(*args):
            request_json = request.get_json()
            if type(request_json) is list:
                result = []
                for js in request_json:
                    obj = class_(**js)
                    result.append(obj)
            else:
                result = class_(**request_json)

            return func(result)
        return decorator
    return wrapper


def request_json_list_mapping(func):
    """This decorator converts any JSON list data in incoming request."""
    @wraps(func)
    def wrapper(*args):
        request_json = request.get_json()
        if type(request_json) is not list:
            raise Exception(f"request body is incorrect.")

        return func(request_json)
    return wrapper


def verify_cls_keywords(cls, **kwargs):
    type_hints = get_type_hints(cls)
    if kwargs.__len__() != type_hints.__len__():
        raise Exception('The data has illegal elements')

    for key, value in type_hints.items():
        element = kwargs.get(key)
        # Validate element exist.
        if element is None:
            raise Exception(f"{key} is necessary.")
            
        # Validate element data type.
        element_type = type(element)
        if element_type is not value:
            try:
                if value is datetime.date:
                    datetime.date.fromisoformat(element)
                elif value is datetime.datetime:
                    datetime.datetime.fromisoformat(element)
                elif value is datetime.time:
                    datetime.time.fromisoformat(element)
                elif value is float and element_type is int:
                    pass
                elif value is float and element_type is decimal.Decimal:
                    pass
                elif value is List[int] and element_type is list:
                    pass
                else:
                    verify_cls_keywords(value, **element)
            except Exception as ex:
                raise Exception(f"The data type of {key} is not correct.")


def verify_kwargs_class_dict(cls, **kwargs):
    type_hints = get_type_hints(cls)

    for key, value in kwargs.items():
        hint_type = type_hints.get(key)
        # Validate element exist.
        if hint_type is None:
            raise Exception(f"{key} is illegal.")

        # Validate element data type.
        element_type = type(value)
        if element_type is not hint_type:
            try:
                if hint_type is datetime.date:
                    datetime.date.fromisoformat(value)
                elif hint_type is datetime.datetime:
                    datetime.datetime.fromisoformat(value)
                elif hint_type is datetime.time:
                    datetime.time.fromisoformat(value)
                elif hint_type is float and element_type is int:
                    pass
                elif hint_type is float and element_type is decimal.Decimal:
                    pass
                elif element_type is list:
                    pass
                else:
                    try:
                        if hint_type._name == 'List':
                            pass
                    except Exception as ex:
                        verify_kwargs_class_dict(hint_type, **value)
            except Exception as ex:
                raise Exception(f"The data type of {key} is not correct.")


class base_json_content(tuple):
    """base tuple object for convert request content with json format to class."""
    # set attribute for all element.
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    # return namedtuple class object.
    def __new__(cls, **kwargs):
        # Validate keyword arguments by hint type.
        verify_kwargs_class_dict(cls, **kwargs)

        return namedtuple(cls.__name__, kwargs).__new__(cls, **kwargs)

from pydantic import BaseModel
class base_dict_model(BaseModel):
    def __getitem__(self, item):
        return getattr(self, item)

    def get(self, key, default=None):
        return self.__dict__.get(key, default)


def check_ip_adress(func):
    def wrapper2(*args, **kwargs):
        if os.getenv('MODE') in ['release']:
            ip = request.access_route[0]
            if socket.gethostbyname(os.getenv('DDNS_URL')) != ip:
                return jsonify(status=False, message="Identify Error", code=401.6), 401
        return func(*args, **kwargs)
    wrapper2.__name__ = func.__name__
    return wrapper2