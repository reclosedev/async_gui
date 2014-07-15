#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.abspath('..'))

import unittest
import time
from async_gui.compat import thread
import multiprocessing

from async_gui.engine import return_result, Engine
#from async_gui.toolkits.pyqt import PyQtEngine as Engine


engine = Engine()
async = engine.async


class EngineTestCase(unittest.TestCase):

    from async_gui.engine import (
        Task, MultiTask, ProcessTask, MultiProcessTask
    )
    testing_gevent = False

    def setUp(self):
        super(EngineTestCase, self).setUp()
        self._main_thread = thread.get_ident()
        self._main_process = multiprocessing.current_process().name

    def test_async(self):
        self.async_method()

    def test_async_with_return_before_yield(self):  # issue 1
        called = [False]

        @async
        def func():
            called[0] = True
            return
            # noinspection PyUnreachableCode
            yield self.Task(shouldnt_call_this)

        def shouldnt_call_this():
            called[0] = False

        func()
        self.assertEquals(called[0], True)

    def test_async_with_result(self):
        @async
        def func():
            r = yield self.Task(self.simple_method)
            return_result(r)
        self.assertEquals(func(), 42)

    def test_async_process(self):
        @async
        def func():
            r = yield self.ProcessTask(mp_func, self._main_process)
            return_result(r)
        self.assertEquals(func(), 42)

    def test_async_multiprocess(self):
        @async
        def func():
            n = 10
            tasks = [self.ProcessTask(mp_func, self._main_process)
                     for _ in range(n)]
            results = yield self.MultiProcessTask(tasks)
            self.assertEquals(results, [42] * n)
            results = yield self.MultiProcessTask(tasks, max_workers=1)
            self.assertEquals(results, [42] * n)
            results = yield tasks
            self.assertEquals(results, [42] * n)
            results = yield (self.Task(self.simple_method),
                             self.Task(self.simple_method))
            self.assertEquals(results, [42] * 2)
        func()

    def test_multitask_unordered(self):
        n = 100

        @async
        def async_exec(tasks, skip_errors):
            gen = yield self.MultiTask(tasks, unordered=True,
                                       skip_errors=skip_errors)
            return_result(list(gen))

        tasks = [self.Task(self.simple_method) for _ in range(n)]
        self.assertEquals(async_exec(tasks, skip_errors=False), [42] * n)
        tasks.append(self.Task(self.throwing, "test"))
        tasks.append(self.Task(self.sleep, 0.1))
        with self.assertRaises(ZeroDivisionError):
            async_exec(tasks, skip_errors=False)
        tasks.append(self.Task(self.throwing, "test"))
        self.assertEquals(len(async_exec(tasks, skip_errors=True)), n + 1)

    @async
    def async_method(self):
        def check_the_same_thread():
            return thread.get_ident() == self._main_thread

        if not self.testing_gevent:
            is_same_thread = yield self.Task(check_the_same_thread)
            self.assertFalse(is_same_thread)
        self.assert_(check_the_same_thread())

        def simple_func():
            return 42

        r1 = yield self.Task(simple_func)
        r2 = yield self.Task(self.simple_method)
        self.assertEqual(r1, r2)
        with self.assertRaises(ZeroDivisionError):
            yield self.Task(self.throwing, "test")

        t = time.time()
        sleep_time = 0.1

        def for_multi(need_raise=False):
            self.sleep(sleep_time)
            if need_raise:
                raise ZeroDivisionError()
            return 42

        tasks = [self.Task(for_multi) for i in range(10)]
        tasks.append(self.Task(for_multi, True))

        with self.assertRaises(ZeroDivisionError):
            yield self.MultiTask(tasks)

        results = yield self.MultiTask(tasks, skip_errors=True)
        self.assertEquals(len(results), len(tasks) - 1)
        self.assert_(time.time() - t < len(tasks) * sleep_time)

        results = yield self.MultiTask(
            [self.Task(for_multi) for _ in range(10)],
            max_workers=2
        )
        self.assertEquals(results, [42] * 10)
        # test pooling, for coverage
        yield self.Task(self.sleep, 0.5)
        # TODO different gui toolkits test for no pool

    def throwing(self, message):
        raise ZeroDivisionError(message)

    def simple_method(self):
        return 42

    def sleep(self, timeout):
        if self.testing_gevent:
            import gevent
            gevent.sleep(timeout)
        else:
            time.sleep(timeout)


def mp_func(caller_name):
    #print(multiprocessing.current_process().name, caller_name)
    return 42


if __name__ == '__main__':
    unittest.main()
