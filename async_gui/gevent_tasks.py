from concurrent import futures
from gevent.pool import Pool
import gevent

from .engine import Task, AllTasks


class GeventExecutor(futures.Executor):

    def __init__(self, max_workers):
        self.max_workers = max_workers
        self._pool = Pool(max_workers)

    def submit(self, fn, *args, **kwargs):
        greenlet = self._pool.spawn(fn, *args, **kwargs)
        return GeventFuture(greenlet)

    def shutdown(self, wait=True):
        self._pool.kill(block=wait)


class GeventFuture(futures.Future):
    def __init__(self, greenlet):
        super(GeventFuture, self).__init__()
        #self._greenlet = gevent.Greenlet()
        self._greenlet = greenlet

    def result(self, timeout=None):
        try:
            return self._greenlet.get(timeout=timeout)
        except gevent.Timeout as e:
            raise futures.TimeoutError(e)

    def exception(self, timeout=None):
        # todo timeout
        return self._greenlet.exception

    def running(self):
        return not self._greenlet.ready()

    def ready(self):
        return self._greenlet.ready()


class GTask(Task):
    executor = GeventExecutor


class AllGTasks(AllTasks):
    executor = GeventExecutor

    def wait(self, executor, tasks, timeout=None):
        executor._pool.join(timeout)
        return all(t.ready() for t in tasks)

