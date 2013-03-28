#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "..")  # hack
import sys
from functools import partial

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
        button = QtGui.QPushButton(
            "Load image",
            clicked=partial(self.do_work,
                            "http://www.google.com/images/srpr/logo4w.png"),
        )
        self.status_label = QtGui.QLabel()
        self.image_label = QtGui.QLabel()
        layout = QtGui.QVBoxLayout(self)
        layout.addWidget(button)
        layout.addWidget(self.status_label)
        layout.addWidget(self.image_label)

    @engine.async
    def do_work(self, url, *args):
        self.status_label.setText("Downloading...")
        data = yield Task(self.load_url, url)
        self.status_label.setText("Done...")
        pixmap = QtGui.QPixmap.fromImage(QtGui.QImage.fromData(data))
        self.image_label.setPixmap(pixmap)

    @engine.async
    def on_button_click(self):
        urls = ['http://www.google.com',
                'http://www.yandex.ru',
                'http://www.python.org']
        result = yield [Task(self.load_url, url) for url in urls]

    def load_url(self, url):
        return urlopen(url).read()


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    engine.set_main_app(app)
    window = MainWidget()
    window.resize(640, 480)
    window.show()
    sys.exit(app.exec_())
