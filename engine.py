#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import types
from functools import wraps
from concurrent import futures

from PyQt4 import QtCore

# TODO way to define gui toolkit
# TODO async could return Runner?
# TODO set_result with exceptions
# TODO multiprocessing
# TODO method to execute something in gui thread
POOL_TIMEOUT = 0.01


class SetResult(Exception):
    def __init__(self, result):
        self.result = result


def async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print func, args, kwargs
        gen = func(*args, **kwargs)
        if isinstance(gen, types.GeneratorType):
            return Runner(gen).run()
    return wrapper


class Task(object):
    executor = futures.ThreadPoolExecutor
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


class MultiTask(Task):
    def __init__(self, tasks, max_workers=None, skip_errors=False):
        self.tasks = list(tasks)
        self.max_workers = max_workers if max_workers else len(self.tasks)
        self.skip_errors = skip_errors

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.tasks)


class MPTask(Task):
    executor = futures.ProcessPoolExecutor


class Runner(object):
    def __init__(self, gen):
        self.gen = gen

    def run(self):
        gen = self.gen
        # start generator and receive first task
        task = gen.next()
        while True:
            try:
                print task
                with task.executor(task.max_workers) as executor:
                    if isinstance(task, MultiTask):
                        task = self._execute_multi_task(gen, executor, task)
                    else:
                        task = self._execute_single_task(gen, executor, task)
            except StopIteration:
                print "stop iteration"
                break
            except SetResult as e:
                # TODO how to terminate generator
                return e.result
            except Exception as exc:
                print "reraising"
                raise

    def _execute_single_task(self, gen, executor, task):
        future = executor.submit(task)
        while True:
            try:
                result = future.result(POOL_TIMEOUT)
            except futures.TimeoutError:
                self.run_gui_loop()
            # TODO canceled error
            except Exception as exc:
                return gen.throw(*sys.exc_info())
            else:
                return gen.send(result)

    def _execute_multi_task(self, gen, executor, task):
        future_tasks = [executor.submit(t) for t in task.tasks]
        while True:
            if futures.wait(future_tasks, POOL_TIMEOUT).not_done:
                self.run_gui_loop()
            else:
                break
        if task.skip_errors:
            results = []
            for f in future_tasks:
                try:
                    results.append(f.result())
                except Exception:
                    pass
        else:
            try:
                results = [f.result() for f in future_tasks]
            except Exception:
                return gen.throw(*sys.exc_info())
        return gen.send(results)

    def run_gui_loop(self):
        # TODO extract this to library specific
        QtCore.QCoreApplication.processEvents(
            QtCore.QEventLoop.AllEvents,
            int(POOL_TIMEOUT * 1000)
        )


def set_result(result):
    raise SetResult(result)





