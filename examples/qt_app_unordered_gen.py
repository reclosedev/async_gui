#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Demo of MultiTask(..., unordered=True) usage.
    In this example, GUI shows list of URLs. When user clicks
    "Get pages size" button, all pages downloaded simultaneously,
    and their info is shown in table when one is ready.
"""
import sys
sys.path.insert(0, "..")  # hack
import time
from collections import namedtuple

from PyQt4 import QtGui

from async_gui import MultiTask
from async_gui.engine import Task
from async_gui.toolkits.pyqt import PyQtEngine


if sys.version_info[0] == 3:
    from urllib.request import urlopen
else:
    from urllib import urlopen


engine = PyQtEngine()


class MainWidget(QtGui.QWidget):

    urls = [
        'http://www.google.com',
        'http://www.yandex.ru',
        'http://www.python.org',
        'http://www.ruby.org',
        'http://twitter.com',
        'http://github.com',
        'http://bitbucket.org',
        'http://stackoverflow.com',
        'http://httpbin.org',
        'http://qt-project.org/',
    ]
    columns = ["Url", "Size, bytes", "Elapsed, seconds"]

    def __init__(self, parent=None):
        super(MainWidget, self).__init__(parent)
        button = QtGui.QPushButton("Get pages size",
                                   clicked=self.on_button_click)
        table = QtGui.QTableWidget()
        table.setColumnCount(len(self.columns))
        table.setHorizontalHeaderLabels(self.columns)
        table.setRowCount(len(self.urls))
        self.url_to_row = {}
        for i, url in enumerate(self.urls):
            item = QtGui.QTableWidgetItem(url)
            table.setItem(i, 0, item)
            self.url_to_row[url] = i
        table.resizeColumnsToContents()
        table.horizontalHeader().setStretchLastSection(True)
        self.urls_table = table

        self.checkBoxUpdateWhenReady = QtGui.QCheckBox(
            "Update when ready",
            checked=True,
        )
        self.status_label = QtGui.QLabel(maximumHeight=15)

        layout = QtGui.QVBoxLayout(self)
        hbox = QtGui.QHBoxLayout()
        hbox.addWidget(self.checkBoxUpdateWhenReady)
        hbox.addWidget(self.status_label)
        layout.addWidget(button)
        layout.addLayout(hbox)
        layout.addWidget(self.urls_table)

    @engine.async
    def on_button_click(self, *args):
        t = time.time()
        self.status_label.setText("Downloading pages...")
        tasks = [Task(self.load_url, url) for url in self.urls]
        use_unordered = self.checkBoxUpdateWhenReady.isChecked()
        results = yield MultiTask(tasks, unordered=use_unordered,
                                  skip_errors=True)
        for url_result in results:
            row = self.url_to_row[url_result.url]
            size_item = QtGui.QTableWidgetItem(str(len(url_result.data)))
            elapsed_item = QtGui.QTableWidgetItem("%.2f" % url_result.elapsed)
            self.urls_table.setItem(row, 1, size_item)
            self.urls_table.setItem(row, 2, elapsed_item)

        self.status_label.setText("Done (%.3f seconds)" % (time.time() - t))

    def load_url(self, url):
        begin = time.time()
        data = urlopen(url).read()
        return UrlResult(url, data, time.time() - begin)

UrlResult = namedtuple("UrlResult", ["url", "data", "elapsed"])

if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    engine.main_app = app
    window = MainWidget()
    window.resize(400, 500)
    window.show()
    sys.exit(app.exec_())
