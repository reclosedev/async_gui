#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore

from ..engine import Engine


class PyQtEngine(Engine):
    def update_gui(self):
        QtCore.QCoreApplication.processEvents(
            QtCore.QEventLoop.AllEvents,
            int(self.pool_timeout * 1000)
        )
