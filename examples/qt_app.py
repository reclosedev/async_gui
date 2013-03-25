#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "..")
from functools import partial
import time
if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen


from PyQt4 import QtCore, QtGui
from async_gui.engine import Task, AllProcessTasks
from async_gui.toolkits.pyqt import PyQtEngine

from cpu_work import is_prime, PRIMES

engine = PyQtEngine()
async = engine.async


class MainWidget(QtGui.QWidget):

    progress_change = QtCore.pyqtSignal(int, int)

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        layout = QtGui.QVBoxLayout(self)
        button = QtGui.QPushButton(
            "Start",
            clicked=partial(self.do_work,
                            "http://www.google.ru/images/srpr/logo4w.png"),
        )
        button2 = QtGui.QPushButton(
            text="Another work",
            clicked=partial(self.do_work,
                            "http://allisonnazarian.com/wp-content/uploads/2012/02/random.jpg"),
        )
        button3 = QtGui.QPushButton(
            text="With progress", clicked=self.with_progress,
        )
        button4 = QtGui.QPushButton(
            text="CPU bound", clicked=self.cpu_bound,
        )
        self.image_label = QtGui.QLabel()
        self.status_label = QtGui.QLabel("Status")
        self.image_result_label = QtGui.QLabel()
        hlayout = QtGui.QHBoxLayout()
        layout.addWidget(button)
        layout.addWidget(button2)
        layout.addWidget(button3)
        layout.addWidget(button4)
        layout.addWidget(self.status_label)
        hlayout.addWidget(self.image_label)
        hlayout.addWidget(self.image_result_label)
        layout.addLayout(hlayout)
        self.progress_dialog = QtGui.QProgressDialog()
        self.progress_change.connect(self.on_progress)
    
    def closeEvent(self, event):
        print("close")
        # TODO how to exit properly?
        #QtGui.QApplication.quit()
        sys.exit(0)

    @async
    def do_work(self, url, *rest):
        self.image_label.clear()
        self.image_result_label.clear()
        self.status_label.setText("Loading...")
        image = yield Task(self.load_image, url)
        pixmap = QtGui.QPixmap.fromImage(image)
        self.image_label.setPixmap(
            pixmap.scaledToWidth(self.image_label.width())
        )
        self.status_label.setText("Calculating histogram...")
        histo_image = yield Task(self.analyze_image, image)
        self.image_result_label.setPixmap(QtGui.QPixmap.fromImage(histo_image))
        self.status_label.setText("Ready")

    def load_image(self, url):
        print("open")
        data = urlopen(url).read()
        print("downloaded", len(data))
        image = QtGui.QImage.fromData(data)
        return image

    @async
    def with_progress(self, checked):
        result = yield Task(self.task_with_progress)
        self.status_label.setText(result)

    @async
    def cpu_bound(self, checked):
        t = time.time()
        self.status_label.setText("calculating...")
        prime_flags = yield AllProcessTasks(
            [Task(is_prime, n) for n in PRIMES],
        )
        print(time.time() - t)
        text = '\n'.join("%s: %s" % (n, prime)
                         for n, prime in zip(PRIMES, prime_flags))
        self.status_label.setText(text)

    def cpu_bound_serial(self, checked):
        t = time.time()
        for i in PRIMES:
            print(is_prime(i))
        print(time.time() - t)

    def on_progress(self, current, maximum):
        self.progress_dialog.setRange(0, maximum - 1)
        self.progress_dialog.setValue(current)

    def task_with_progress(self):
        n = 100
        for i in range(n):
            self.progress_change.emit(i, n)
            if self.progress_dialog.wasCanceled():
                self.progress_dialog.reset()
                return "canceled"
            time.sleep(0.05)
        return "42"

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
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
