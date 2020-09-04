#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# Author Xu Junkai
# coding=utf-8
# @Time    : 2020/9/3 22:53
# @Site    :
# @File    : strech_threadpoolexcutor.py
# @Software: PyCharm
"""
import concurrent
from strech_thread_pool.threadpool_excutor import BoundedThreadPoolExecutor

def monkey_patch_concurrent_futeres_threadpoolexecutor():
    concurrent.futures.ThreadPoolExecutor = BoundedThreadPoolExecutor


if __name__ == '__main__':
    monkey_patch_concurrent_futeres_threadpoolexecutor()  # 如果不大猴子补丁，出错了自己完全不知道。
    from concurrent.futures import ThreadPoolExecutor

    def test_error():
        raise ValueError('测试错误')

    pool = ThreadPoolExecutor(20)
    pool.submit(test_error)
