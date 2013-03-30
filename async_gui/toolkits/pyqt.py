#!/usr/bin/env python
# -*- coding: utf-8 -*-
from PyQt4 import QtCore

from ._qt import QtEngine


class PyQtEngine(QtEngine):
    QtCore = QtCore