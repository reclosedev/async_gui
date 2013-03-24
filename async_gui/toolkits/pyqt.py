#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore

from ..engine import Engine, POOL_TIMEOUT


class PyQtEngine(Engine):
    def __init__(self, pool_timeout=POOL_TIMEOUT):
        super(PyQtEngine, self).__init__(pooling_function, pool_timeout)


def pooling_function(timeout):
    QtCore.QCoreApplication.processEvents(
        QtCore.QEventLoop.AllEvents,
        int(timeout * 1000)
    )
