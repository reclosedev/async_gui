#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import types
import time
from functools import wraps
from concurrent import futures
import multiprocessing
# TODO method to execute something in gui thread
# TODO separate engine, tasks
# TODO should i call multiprocessing.freeze_support() ?
# TODO documentation
# TODO remove prints


POOL_TIMEOUT = 0.02


class SetResult(Exception):
    def __init__(self, result):
        self.result = result


class Engine(object):
    def __init__(self, pool_timeout=POOL_TIMEOUT):
        self.pool_timeout = pool_timeout
        self.main_app = None

    def async(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            gen = func(*args, **kwargs)
            if isinstance(gen, types.GeneratorType):
                return self.create_runner(gen).run()
        return wrapper

    def create_runner(self, gen):
        return Runner(self, gen)

    def set_main_app(self, app):
        self.main_app = app

    def update_gui(self):
        return time.sleep(self.pool_timeout)


class Task(object):
    # TODO maybe executor_class?
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


class ProcessTask(Task):
    executor = futures.ProcessPoolExecutor


# TODO better names
class AllTasks(Task):
    def __init__(self, tasks, max_workers=None, skip_errors=False):
        self.tasks = list(tasks)
        self.max_workers = max_workers if max_workers else len(self.tasks)
        self.skip_errors = skip_errors

    def __repr__(self):
        return '<%s(%s)>' % (self.__class__.__name__, self.tasks)

    # TODO maybe it could accept only executor and timeout
    def wait(self, executor, tasks, timeout=None):
        """ Return True if all done, False otherwise
        """
        return not futures.wait(tasks, timeout).not_done


class AllProcessTasks(AllTasks):
    executor = futures.ProcessPoolExecutor

    def __init__(self, tasks, max_workers=None, skip_errors=False, **kwargs):
        # None for ProcessPoolExecutor means cpu count
        if max_workers is None:
            max_workers = multiprocessing.cpu_count()
        super(AllProcessTasks, self).__init__(
            tasks, max_workers, skip_errors, **kwargs
        )


class Runner(object):
    def __init__(self, engine, gen):
        self.engine = engine
        self.gen = gen

    def run(self):
        gen = self.gen
        # start generator and receive first task
        task = next(gen)
        while True:
            try:
                if isinstance(task, (list, tuple)):
                    assert len(task), "Empty tasks sequence"
                    tasks = task
                    first_task = tasks[0]
                    if isinstance(first_task, ProcessTask):
                        task = AllProcessTasks(tasks)
                    else:
                        task = AllTasks(tasks)
                    # TODO gevent tasks?

                with task.executor(task.max_workers) as executor:
                    if isinstance(task, AllTasks):
                        task = self._execute_multi_task(gen, executor, task)
                    else:
                        task = self._execute_single_task(gen, executor, task)
            except StopIteration:
                break
            except SetResult as e:
                gen.close()
                return e.result
            except Exception as exc:
                print("reraising")
                raise

    def _execute_single_task(self, gen, executor, task):
        future = executor.submit(task)
        while True:
            try:
                result = future.result(self.engine.pool_timeout)
            except futures.TimeoutError:
                self.engine.update_gui()
            # TODO canceled error
            except Exception:
                return gen.throw(*sys.exc_info())
            else:
                return gen.send(result)

    def _execute_multi_task(self, gen, executor, task):
        future_tasks = [executor.submit(t) for t in task.tasks]
        while True:
            if not task.wait(executor, future_tasks, self.engine.pool_timeout):
                self.engine.update_gui()
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


def set_result(result):
    raise SetResult(result)





