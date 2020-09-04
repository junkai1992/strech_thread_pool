#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# Author Xu Junkai
# coding=utf-8
# @Time    : 2020/9/3 22:42
# @Site    :
# @File    : threadpool_excutor.py
# @Software: PyCharm
"""
from functools import wraps
import queue
from concurrent.futures import ThreadPoolExecutor

def decorator(func):
    @wraps(func)
    def inner(*args,**kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print("执行线程发生错误:{}".format(e))
    return inner

class BoundedThreadPoolExecutor(ThreadPoolExecutor):
    def __init__(self, max_workers=None, thread_name_prefix=""):
        ThreadPoolExecutor.__init__(self, max_workers, thread_name_prefix)
        self._work_queue = queue.Queue(max_workers * 2)
    def submit(self, fn, *args, **kwargs):
        fn_decorator = decorator(fn)
        super().submit(fn_decorator, *args, **kwargs)


if __name__ == '__main__':
    def fun():
        print(1 / 0)
    pool = BoundedThreadPoolExecutor(10)
    pool.submit(fun)
