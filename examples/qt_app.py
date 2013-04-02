#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "..")  # hack
import time
from async_gui import MultiProcessTask
from examples.cpu_work import is_prime, PRIMES

from PyQt4 import QtGui
from async_gui.engine import Task
from async_gui.toolkits.pyqt import PyQtEngine

if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen


engine = PyQtEngine()


class MainWidget(QtGui.QWidget):

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        button = QtGui.QPushButton("Load image", clicked=self.on_button_click)
        button2 = QtGui.QPushButton("Check primes", clicked=self.check_primes)
        self.status_label = QtGui.QLabel()
        self.image_label = QtGui.QLabel()
        self.result_label = QtGui.QLabel()
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(button)
        layout.addWidget(button2)
        layout.addWidget(self.status_label)
        layout.addWidget(self.result_label)
        layout.addWidget(self.image_label)

    @engine.async
    def on_button_click(self, *args):
        self.status_label.setText("Downloading image...")
        # Run single task in separate thread
        image_data = yield Task(self.load_url,
                                "http://www.google.com/images/srpr/logo4w.png")
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage.fromData(image_data))
        self.image_label.setPixmap(pixmap)
        self.status_label.setText("Downloading pages...")
        urls = ['http://www.google.com',
                'http://www.yandex.ru',
                'http://www.python.org']
        # Run multiple task simultaneously in thread pool
        pages = yield [Task(self.load_url, url) for url in urls]
        self.status_label.setText("Done")
        avg_size = sum(map(len, pages)) / len(pages)
        self.result_label.setText("Average page size: %s" % avg_size)

    def load_url(self, url):
        return urlopen(url).read()

    @engine.async
    def check_primes(self, checked):
        t = time.time()
        self.status_label.setText("Checking primes...")
        prime_flags = yield MultiProcessTask(
            [Task(is_prime, n) for n in PRIMES],
        )
        self.status_label.setText("Elapsed: %.3f seconds" % (time.time() - t))
        text = '\n'.join("%s: %s" % (n, prime)
                         for n, prime in zip(PRIMES, prime_flags))
        self.result_label.setText(text)


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    engine.main_app = app
    window = MainWidget()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())
