#!/usr/bin/env python
# -*- coding:utf-8 -*-
"""
# Author Xu Junkai
# coding=utf-8
# @Time    : 2020/9/3 23:00
# @Site    :
# @File    : sharp_threadpoolexecutor.py.py
# @Software: PyCharm
"""
import os
import atexit
import sys
import threading
import time
import queue
import weakref


_closed = False
_threads_queues = weakref.WeakKeyDictionary()


def _python_exit():
    global _closed
    for t,q in list(_threads_queues.items()):
        q.put(None)
    for t,q in list(_threads_queues.items()):
        t.join()

atexit.register(_python_exit)



class _WorkItem(object):
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
    def run(self):
        try:
            self.func(*self.args,**self.kwargs)
        except BaseException as err:
            print("运行发生异常:",err)
    def __repr__(self):
        return "{}_{}_{}".format(self.func.__name__, self.args, self.kwargs)



class ThreadPoolExecutorStrech(object):
    MIN_WORKERS = 5
    KEEP_ALIVE_TIME = 30

    def __init__(self, max_workers=None, thread_name_prefix=""):
        self._max_workers = max_workers or 4
        self._thread_name_prefix = thread_name_prefix
        self.work_queue = queue.Queue(max_workers)
        # self._threads = set()
        self._threads = weakref.WeakSet()
        self._lock_compute_threads_free_count = threading.Lock()
        self.threads_free_count = 0
        self._shutdown = False
        self._shutdown_lock = threading.Lock()

    def _change_threads_free_count(self, change_num):
        with self._lock_compute_threads_free_count:
            self.threads_free_count += change_num

    def submit(self, fn, *args, **kwargs):
        with self._shutdown_lock:
            if self._shutdown:
                raise RuntimeError('无法添加新的任务到线程池中...')
        self._adjust_thread_count()
        self.work_queue.put(_WorkItem(fn, args, kwargs))

    def _adjust_thread_count(self):
        print("线程池中不在工作中线程数:{}.线程存在引用数量:{}.线程队列中数量:{}.当前活跃线程数量:{}.".format(self.threads_free_count, len(self._threads), len(_threads_queues), get_current_threads_num()))
        if self.threads_free_count < self.MIN_WORKERS and len(self._threads) < self._max_workers:
            t = _CustomThread(self)
            t.setDaemon(True)
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self.work_queue

    def shutdown(self, wait=True):
        with self._shutdown_lock:
            self._shutdown = True
            self.work_queue.put(None)
        if wait:
            for t in self._threads:
                t.join()
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(wait=True)
        return False


CustomThreadpoolExecutor = ThreadPoolExecutorStrech


class _CustomThread(threading.Thread):
    def __init__(self, executorx: ThreadPoolExecutorStrech):
        super().__init__()
        self._executorx = executorx
    def _remove_thread(self, stop_reason=""):
        print("停止线程{},触发条件{}".format(self._ident,stop_reason))
        self._executorx._change_threads_free_count(-1)
        self._executorx._threads.remove(self)
        _threads_queues.pop(self)
    def run(self):
        print("启动线程:{}".format(self._ident))
        self._executorx._change_threads_free_count(1)
        while True:
            try:
                work_item = self._executorx.work_queue.get(block=True, timeout=self._executorx.KEEP_ALIVE_TIME)
            except queue.Empty:
                # continue
                # self._remove_thread()
                # break
                if self._executorx.threads_free_count > self._executorx.MIN_WORKERS:
                    self._remove_thread(
                        '当前线程超过 {} 秒没有任务，线程池中不在工作状态中的线程数量是{}，超过了指定的数量 {}'.format(self._executorx.KEEP_ALIVE_TIME,self._executorx.threads_free_count,self._executorx.MIN_WORKERS))
                    break  # 退出while 1，即是结束。这里才是决定线程结束销毁，_remove_thread只是个名字而已，不是由那个来销毁线程。
                else:
                    continue
            if work_item is not None:
                self._executorx._change_threads_free_count(-1)
                work_item.run()
                del work_item
                self._executorx._change_threads_free_count(1)
                continue
            if _closed or self._executorx._shutdown:
                self._executorx.work_queue.put(None)
                break

process_name_set = set()


def show_current_threads_num(sleep_time=600, process_name="", block=False, daemon=True):
    process_name = sys.argv[0] if process_name == '' else process_name
    def _show_current_threads_num():
        while True:
            print("{}-{}进程的线程数量是:{}".format(process_name, os.getpid(),threading.active_count()))
            time.sleep(sleep_time)
    if process_name not in process_name_set:
        if block:
            _show_current_threads_num()
        else:
            t = threading.Thread(target = _show_current_threads_num, daemon=daemon)
            t.start()
        process_name_set.add(process_name)


def get_current_threads_num():
    return threading.active_count()


if __name__ == '__main__':
    from concurrent.futures import ThreadPoolExecutor
    show_current_threads_num(sleep_time=5)
    def f1(a):
        time.sleep(0.2)  # 可修改这个数字测试多线程数量调节功能。
        print(a)
        # nb_print(f'{a} 。。。。。。。')
        # raise Exception('抛个错误测试')  # 官方的不会显示函数出错你，你还以为你写的代码没毛病呢。


    # pool = ThreadPoolExecutorShrinkAble(200)
    pool = ThreadPoolExecutor(200)  # 测试对比官方自带

    for i in range(300):
        time.sleep(0.3)  # 这里的间隔时间模拟，当任务来临不密集，只需要少量线程就能搞定f1了，因为f1的消耗时间短，
        # 不需要开那么多线程，CustomThreadPoolExecutor比ThreadPoolExecutor 优势之一。
        pool.submit(f1, str(i))

    # 1/下面测试阻塞主线程退出的情况。注释掉可以测主线程退出的情况。
    # 2/此代码可以证明，在一段时间后，连续长时间没任务，官方线程池的线程数目还是保持在最大数量了。而此线程池会自动缩小，实现了java线程池的keppalivetime功能。
    time.sleep(1000000)
