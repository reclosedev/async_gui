#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import time
import thread
import multiprocessing

from async_gui.engine import (
    Engine, Task, AllTasks, set_result,
    ProcessTask, AllProcessTasks
)
from async_gui.toolkits.pyqt import PyQtEngine as Engine

eng = Engine()
async = eng.async

class EngineTestCase(unittest.TestCase):

    def setUp(self):
        super(EngineTestCase, self).setUp()
        self._main_thread = thread.get_ident()
        self._main_process = multiprocessing.current_process().name

    def test_async(self):
        self.async_method()

    def test_async_with_result(self):
        @async
        def func():
            r = yield Task(self.simple_method)
            set_result(r)
        self.assertEquals(func(), 42)

    def test_async_process(self):
        @async
        def func():
            r = yield ProcessTask(mp_func, self._main_process)
            set_result(r)
        self.assertEquals(func(), 42)

    def test_async_multiprocess(self):
        @async
        def func():
            n = 10
            tasks = [ProcessTask(mp_func, self._main_process)
                     for _ in range(n)]
            results = yield AllProcessTasks(tasks)
            self.assertEquals(results, [42] * n)
            results = yield AllProcessTasks(tasks, max_workers=1)
            self.assertEquals(results, [42] * n)
            results = yield tasks
            self.assertEquals(results, [42] * n)
            results = yield (Task(self.simple_method),
                             Task(self.simple_method))
            self.assertEquals(results, [42] * 2)
        func()

    @async
    def async_method(self):
        def check_the_same_thread():
            return thread.get_ident() == self._main_thread

        is_same_thread = yield Task(check_the_same_thread)
        self.assertFalse(is_same_thread)
        self.assert_(check_the_same_thread())

        def simple_func():
            return 42

        r1 = yield Task(simple_func)
        r2 = yield Task(self.simple_method)
        self.assertEqual(r1, r2)
        with self.assertRaises(Exception):
            yield Task(self.throwing, "test")

        t = time.time()
        sleep_time = 0.1

        def for_multi(need_raise=False):
            print thread.get_ident()
            time.sleep(sleep_time)
            if need_raise:
                raise Exception()
            return 42

        tasks = [Task(for_multi) for i in range(10)]
        tasks.append(Task(for_multi, True))

        with self.assertRaises(Exception):
            yield AllTasks(tasks)

        results = yield AllTasks(tasks, skip_errors=True)
        self.assertEquals(len(results), len(tasks) - 1)
        self.assert_(time.time() - t < len(tasks) * sleep_time)

        results = yield AllTasks([Task(for_multi) for _ in range(10)],
                                  max_workers=2)
        self.assertEquals(results, [42] * 10)
        # test pooling, for coverage
        yield Task(time.sleep, 0.5)
        # TODO different gui toolkits test for no pool

    def throwing(self, message):
        raise Exception(message)

    def simple_method(self):
        return 42


def mp_func(caller_name):
    print multiprocessing.current_process().name, caller_name
    return 42


if __name__ == '__main__':
    unittest.main()
