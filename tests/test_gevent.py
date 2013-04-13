#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import unittest
import time
import urllib
try:
    from gevent.monkey import patch_socket
except ImportError:
    print("Gevent not installed")
else:
    patch_socket()
    from async_gui.gevent_tasks import MultiGTask
    from tests.test_engine import EngineTestCase, engine, async


    class GeventExecutorTestCase(EngineTestCase):
        from async_gui.gevent_tasks import GTask as Task
        from async_gui.gevent_tasks import MultiGTask as AllTasks

        testing_gevent = True

        def test_gevent_urllib(self):
            self.gevent_with_urllib()

        @async
        def gevent_with_urllib(self):

            def download(url):
                return urllib.urlopen(url).read()

            delay = 1
            n = 5
            t = time.time()
            urls = ["http://httpbin.org/delay/%s" % delay for _ in range(n)]
            result = yield MultiGTask([self.Task(download, url) for url in urls])
            result2 = yield [self.Task(download, url) for url in urls]
            elapsed = time.time() - t
            self.assertEqual(len(result), n)
            self.assertLess(elapsed, delay * n)
            print(elapsed)


if __name__ == '__main__':
    unittest.main()
