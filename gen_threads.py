#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
import functools
import types
from concurrent import futures
import multiprocessing
import pickle
import sys
import urllib

from PyQt4 import QtCore, QtGui
import time
import thread
import threading
from functools import partial, wraps


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
        if max_workers is None:
            max_workers = len(self.tasks)
        self.max_workers = max_workers
        self.skip_errors = skip_errors

    def __repr__(self):
        return ('<%s(%s)>' %
                (self.__class__.__name__, self.tasks))


class MPTask(Task):
    executor = futures.ProcessPoolExecutor

POOL_TIMEOUT = 0.01

def engine(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print func, args, kwargs
        gen = func(*args, **kwargs)
        if isinstance(gen, types.GeneratorType):
            Runner(gen).run()
    return wrapper


class Runner(object):
    def __init__(self, gen):
        self.gen = gen

    def run(self):
        gen = self.gen
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
    pass


def print_thread(message=""):
    print message, "in thread", thread.get_ident()


class MainWidget(QtGui.QWidget):
    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)
        button = QtGui.QPushButton(
            "Start",
            clicked=partial(self.do_work,
                            "https://www.google.ru/images/srpr/logo4w.png"),
        )
        button2 = QtGui.QPushButton(
            text="Another work",
            clicked=partial(self.do_work,
                            "http://allisonnazarian.com/wp-content/uploads/2012/02/random.jpg"),
        )
        self.image_label = QtGui.QLabel()
        self.status_label = QtGui.QLabel("Status")
        self.image_result_label = QtGui.QLabel()
        hlayout = QtGui.QHBoxLayout()
        layout.addWidget(button)
        layout.addWidget(button2)
        layout.addWidget(self.status_label)
        hlayout.addWidget(self.image_label)
        hlayout.addWidget(self.image_result_label)
        layout.addLayout(hlayout)

    @engine
    def do_work(self, url, *rest):
        print_thread("gui")
        self.image_label.clear()
        self.image_result_label.clear()
        self.status_label.setText("Loading...")
        image = yield Task(self.load_image, url)
        print image
        #time.sleep(1)
        pixmap = QtGui.QPixmap.fromImage(image).scaledToWidth(200)
        self.image_label.setPixmap(pixmap)

        try:
            num = yield Task(self.with_error)
        except ZeroDivisionError:
            print "can handle exceptions"

        self.status_label.setText("Calculating histogram...")
        histo_image = yield Task(analyze_image, image)
        self.image_result_label.setPixmap(QtGui.QPixmap.fromImage(histo_image))
        self.status_label.setText("Ready")
        try:
            results = yield MultiTask(Task(self.for_multi, i) for i in range(10))
            print results
        except ZeroDivisionError:
            print "ZERO"
        results = yield MultiTask([Task(self.for_multi, i) for i in range(10)],
                                  skip_errors=True)
        print results




    def load_image(self, url):
        print "open"
        data = urllib.urlopen(url).read()
        print "downloaded", len(data)
        image = QtGui.QImage.fromData(data)
        return image

    def with_error(self):
        return 1/0

    def for_multi(self, i):
        print "multi", i
        time.sleep(1)
        return float(1) / (5 - i)


def analyze_image(image, height=200):
    print "analyze"
    histogram = [0] * 256
    for i in range(image.width()):
        for j in range(image.height()):
            color = QtGui.QColor(image.pixel(i, j))
            histogram[color.lightness()] += 1

    max_value = max(histogram)
    scale = float(height) / max_value
    width = len(histogram)
    print scale, width, max_value
    histo_img = QtGui.QImage(
        QtCore.QSize(width, height),
        QtGui.QImage.Format_ARGB32
    )
    print histo_img
    histo_img.fill(QtCore.Qt.white)
    p = QtGui.QPainter()
    p.begin(histo_img)
    for i, value in enumerate(histogram):
        y = height - int(value * scale)
        p.drawLine(i, height, i, y)
    p.end()
    return histo_img


def main():
    app = QtGui.QApplication(sys.argv)
    window = MainWidget()
    window.resize(640, 480)
    window.show()
    print 'after start'
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()


