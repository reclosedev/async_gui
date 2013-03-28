#!/usr/bin/env python
# -*- coding: utf-8 -*-
""" Core of library... TODO
"""
import sys
import types
import time
from functools import wraps
from concurrent import futures

from .tasks import Task, MultiTask, ProcessTask, MultiProcessTask
try:
    # needed for type checks for list of tasks
    from .gevent_tasks import GTask, MultiGTask
except ImportError:
    GTask = MultiGTask = None
# TODO method to execute something in gui thread
# TODO should i call multiprocessing.freeze_support() ?
# TODO documentation
# TODO callbacks
# TODO cancel tasks, or stop engine


POOL_TIMEOUT = 0.02


class ReturnResult(Exception):
    """ Used to return result from generator
    """
    def __init__(self, result):
        super(ReturnResult, self).__init__()
        self.result = result


class Engine(object):
    """ Engine base class

    Subclasses should implement :meth:`update_gui`.
    Contains decorator for functions with async calls :meth:`async`.
    After creating engine instance, call :meth:`set_main_app` (not needed on
    PyQt/PySide)
    """
    def __init__(self, pool_timeout=POOL_TIMEOUT):
        """
        :param pool_timeout: time in seconds which GUI will spend in loop
                             now works only in PyQt/PySide
        """
        self.pool_timeout = pool_timeout
        #: main application instance
        self.main_app = None

    def async(self, func):
        """ Decorator for asynchronous generators.

        Any :class:`Task`, :class:`ProcessTask` or :class:`GTask` yielded from
        generator will be executed in separate thread, process or greenlet
        accordingly. For example gui application can has following button
        click handler::

            engine = PyQtEngine()
            ...
            @engine.async
            def on_button_click():
                # do something in GUI thread
                data = yield Task(do_time_consuming_work, param)
                update_gui_with(data)  # in main GUI thread
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            gen = func(*args, **kwargs)
            if isinstance(gen, types.GeneratorType):
                return self.create_runner(gen).run()
        return wrapper

    def create_runner(self, gen):
        """ Returns :class:`Runner` instance

        :param gen: generator which returns async tasks
        """
        return Runner(self, gen)

    def set_main_app(self, app):
        """ Saves reference to GUI application instance
        """
        self.main_app = app

    def update_gui(self):
        """ Allows GUI to process events
        """
        return time.sleep(self.pool_timeout)


class Runner(object):
    """ Runs tasks returned by generator
    """
    def __init__(self, engine, gen):
        """
        :param engine: :class:`Engine` instance
        :param gen: Generator which yields tasks
        """
        self.engine = engine
        self.gen = gen

    def run(self):
        # TODO document details in module level docs
        """ Runs tasks

        If some task raises :class:`ReturnResult`, returns it's value...
        :return: :raise:
        """
        gen = self.gen
        task = next(gen)  # start generator and receive first task
        while True:
            try:
                if isinstance(task, (list, tuple)):
                    assert len(task), "Empty tasks sequence"
                    first_task = task[0]
                    if isinstance(first_task, ProcessTask):
                        task = MultiProcessTask(task)
                    elif GTask and isinstance(first_task, GTask):
                        task = MultiGTask(task)
                    else:
                        task = MultiTask(task)

                with task.executor_class(task.max_workers) as executor:
                    if isinstance(task, MultiTask):
                        task = self._execute_multi_task(gen, executor, task)
                    else:
                        task = self._execute_single_task(gen, executor, task)
            except StopIteration:
                break
            except ReturnResult as e:
                gen.close()
                return e.result

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


def return_result(result):
    """ Allows to return result from generator

    Internally it raises :class:`ReturnResult` exception, so take in mind, that
    it can be catched in catch all block
    """
    raise ReturnResult(result)
