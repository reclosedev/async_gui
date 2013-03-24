#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
import time
import thread

from engine import async, Task, MultiTask


class EngineTestCase(unittest.TestCase):

    def setUp(self):
        super(EngineTestCase, self).setUp()
        self._main_thread = thread.get_ident()

    def test_async(self):
        self.async_method()
        #self.assertEqual(True, False)

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

        def for_multi_raises(need_raise=False):
            time.sleep(sleep_time)
            if need_raise:
                raise Exception()
            return i

        tasks = [Task(for_multi_raises) for i in range(10)]
        tasks.append(Task(for_multi_raises, True))

        with self.assertRaises(Exception):
            yield MultiTask(tasks)

        results = yield MultiTask(tasks, skip_errors=True)
        self.assertEquals(len(results), len(tasks) - 1)
        self.assert_(time.time() - t < len(tasks) * sleep_time)

        results = yield MultiTask(Task(simple_func) for _ in range(10))
        self.assertEquals(results, [42] * 10)
        yield Task(time.sleep, 0.5)
        # TODO different gui toolkits test for no pool


    def throwing(self, message):
        raise Exception(message)

    def simple_method(self):
        return 42

if __name__ == '__main__':
    unittest.main()
