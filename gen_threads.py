#!/usr/bin/env python
# -*- coding: utf-8 -*-
from collections import defaultdict
import functools
import multiprocessing
import sys
import urllib

from PyQt4 import QtCore, QtGui
import time
import thread
import threading
from functools import partial, wraps


class BaseExecutor(object):
    def __init__(self, task):
        self.task = task
        self.done = self.create_event()
        self.result = None

    def start(self):
        self.execute()

    def execute(self):
        self.result = self.task.execute()
        self.done.set()

    def is_ready(self):
        return self.done.is_set()

    def wait_ready(self, timeout=None):
        self.done.wait(timeout)

    def create_event(self, *args, **kwargs):
        return threading.Event(*args, **kwargs)


class QThreadRunner(QtCore.QThread):
    def __init__(self, task, parent=None):
        QtCore.QThread.__init__(self, parent)
        self.task = task

    def run(self):
        self.task()


class QThreadExecutor(BaseExecutor):
    def __init__(self, task):
        super(QThreadExecutor, self).__init__(task)
        self._thread = QThreadRunner(super(QThreadExecutor, self).execute)

    def start(self):
        self._thread.start()


class MPExecutor(BaseExecutor):
    def __init__(self, task):
        super(MPExecutor, self).__init__(task)
        self._process = multiprocessing.Process(
            target=super(MPExecutor, self).execute
        )

    def start(self):
        self._process.start()

    def create_event(self, *args, **kwargs):
        return multiprocessing.Event()


class Task(object):
    executor = QThreadExecutor

    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs

    def execute(self):
        return self.func(*self.args, **self.kwargs)

    def __repr__(self):
        return ('Task(%s, %r, %r)' %
                (self.func.__name__, self.args, self.kwargs))


class MPTask(Task):
    executor = MPExecutor

POOL_TIMEOUT = 0.01

def engine(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        print func, args, kwargs
        gen = func(*args, **kwargs)
        result = None
        while True:
            try:
                task = gen.send(result)
                print task
                try:
                    executor = task.executor(task)
                    executor.start()
                    while not executor.is_ready():
                        QtCore.QCoreApplication.processEvents(
                            QtCore.QEventLoop.AllEvents,
                            int(POOL_TIMEOUT * 1000))
                        executor.wait_ready(POOL_TIMEOUT)
                    result = executor.result
                except Exception as e:
                    print e
                    break
            except StopIteration:
                print "stop iteration"
                break
            except Exception as exc:
                print exc
        pass
    return wrapper


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
        #time.sleep(1)
        pixmap = QtGui.QPixmap.fromImage(image).scaledToWidth(200)
        self.image_label.setPixmap(pixmap)
        self.status_label.setText("Calculating histogram...")
        histo_image = yield Task(self.analyze_image, image)
        self.image_result_label.setPixmap(QtGui.QPixmap.fromImage(histo_image))
        self.status_label.setText("Ready")

    def load_image(self, url):
        print_thread("heavy")
        print "open"
        data = urllib.urlopen(url).read()
        print "downloaded", len(data)
        image = QtGui.QImage.fromData(data)
        return image

    def analyze_image(self, image, height=200):
        histogram = [0] * 256
        for i in range(image.width()):
            for j in range(image.height()):
                color = QtGui.QColor(image.pixel(i, j))
                histogram[color.lightness()] += 1
        max_value = max(histogram)
        scale = float(height) / max_value
        width = len(histogram)
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


