#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import types
import time
from functools import wraps
from concurrent import futures

from .tasks import Task, AllTasks, ProcessTask, AllProcessTasks
try:
    # needed for type checks for list of tasks
    from .gevent_tasks import GTask, AllGTasks
except ImportError:
    GTask = AllGTasks = None
# TODO method to execute something in gui thread
# TODO should i call multiprocessing.freeze_support() ?
# TODO documentation


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


class Runner(object):
    def __init__(self, engine, gen):
        self.engine = engine
        self.gen = gen

    def run(self):
        gen = self.gen
        task = next(gen)  # start generator and receive first task
        while True:
            try:
                if isinstance(task, (list, tuple)):
                    assert len(task), "Empty tasks sequence"
                    tasks = task
                    first_task = tasks[0]
                    if isinstance(first_task, ProcessTask):
                        task = AllProcessTasks(tasks)
                    elif GTask and isinstance(first_task, GTask):
                        task = AllGTasks(tasks)
                    else:
                        task = AllTasks(tasks)
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





