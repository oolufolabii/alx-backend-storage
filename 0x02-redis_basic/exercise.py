#!/usr/bin/env python3
'''Python module for using the Redis NoSQL data storage.
'''
import uuid
import redis
from functools import wraps
from typing import Any, Callable, Union


def count_calls(method: Callable) -> Callable:
    '''Tracks the number of calls made to a method in a Cache class.
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''Invokes the given method after incrementing its call counter.
        '''
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return invoker


def call_history(method: Callable) -> Callable:
    '''Tracks the call details of a method in a Cache class.
    '''
    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        '''Returns the method's output after storing its inputs and output.
        '''
        input_key = '{}:inputs'.format(method.__qualname__)
        output_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(input_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(output_key, output)
        return output
    return invoker


def replay(fn: Callable) -> None:
    '''Displays the call history of a Cache class' method.
    '''
    if fn is None or not hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    function_name = fn.__qualname__
    input_key = '{}:inputs'.format(function_name)
    output_key = '{}:outputs'.format(function_name)
    function_call_count = 0
    if redis_store.exists(function_name) != 0:
        function_call_count = int(redis_store.get(function_name))
    print('{} was called {} times:'.format(function_name, function_call_count))
    function_inputs = redis_store.lrange(input_key, 0, -1)
    function_outputs = redis_store.lrange(output_key, 0, -1)
    for function_input, function_output in zip(function_inputs, function_outputs):
        print('{}(*{}) -> {}'.format(
            function_name,
            function_input.decode("utf-8"),
            function_output,
        ))


class Cache:
    '''Creates an object for storing data in a Redis data storage.
    '''
    def __init__(self) -> None:
        '''Initializes a Cache instance.
        '''
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        '''Stores a value in a Redis data storage and returns the key.
        '''
        data_key = str(uuid.uuid4())
        self._redis.set(data_key, data)
        return data_key

    def get(
            self,
            key: str,
            function: Callable = None,
            ) -> Union[str, bytes, int, float]:
        '''Return a value from a Redis data storage.
        '''
        data = self._redis.get(key)
        return function(data) if function is not None else data

    def get_str(self, key: str) -> str:
        '''Return a string value from a Redis data storage.
        '''
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        '''Return an integer value from a Redis data storage.
        '''
        return self.get(key, lambda x: int(x))
