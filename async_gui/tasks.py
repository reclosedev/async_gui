#!/usr/bin/env python
# -*- coding: utf-8 -*-
import multiprocessing
from concurrent import futures


class Task(object):

    executor_class = futures.ThreadPoolExecutor
    max_workers = 1

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def start(self):
        return self.func(*self.args, **self.kwargs)

    __call__ = start

    def __repr__(self):
        return ('<%s(%s, %r, %r)>' %
                (self.__class__.__name__, self.func.__name__,
                 self.args, self.kwargs))


class ProcessTask(Task):
    executor_class = futures.ProcessPoolExecutor


class MultiTask(Task):
    def __init__(self, tasks, max_workers=None, skip_errors=False):
        self.tasks = list(tasks)
        self.max_workers = max_workers if max_workers else len(self.tasks)
        self.skip_errors = skip_errors

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.tasks)

    # TODO maybe it could accept only executor_class and timeout
    def wait(self, executor, tasks, timeout=None):
        """ Return True if all done, False otherwise
        """
        return not futures.wait(tasks, timeout).not_done


class MultiProcessTask(MultiTask):
    executor_class = futures.ProcessPoolExecutor

    def __init__(self, tasks, max_workers=None, skip_errors=False, **kwargs):
        # None for ProcessPoolExecutor means cpu count
        if max_workers is None:
            max_workers = multiprocessing.cpu_count()
        super(MultiProcessTask, self).__init__(
            tasks, max_workers, skip_errors, **kwargs
        )
