#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
sys.path.insert(0, os.path.abspath('..'))
import unittest
import time

from async_gui.engine import Task


class ToolkitsTestCase(unittest.TestCase):

    def test_kivy(self):
        try:
            from async_gui.toolkits.kivy import KivyEngine
            from kivy.app import App
            from kivy.clock import Clock
        except ImportError:
            return self.skipTest("Kivy not installed")

        called = [False]
        root = App()
        Clock.schedule_once(lambda e: self._check_toolkit( KivyEngine,
                            root, root.stop, called))
        root.run()
        self.assertTrue(called[0])

    def test_pyqt(self):
        try:
            from async_gui.toolkits.pyqt import PyQtEngine
            from PyQt4 import QtCore
        except ImportError:
            return self.skipTest("PyQt not installed")
        self._check_qt(PyQtEngine, QtCore)
        self._check_qt(PyQtEngine, QtCore, without_app=True)

    def test_pyside(self):
        try:
            from async_gui.toolkits.pyside import PySideEngine
            from PySide import QtCore
        except ImportError:
            return self.skipTest("PySide not installed")
        self._check_qt(PySideEngine, QtCore)

    def _check_qt(self, engine_class, QtCore, without_app=False):
        called = [False]
        app = QtCore.QCoreApplication([])
        app_arg = app if not without_app else None
        QtCore.QTimer.singleShot(
            0,
            lambda: self._check_toolkit(engine_class, app_arg,
                QtCore.QCoreApplication.quit, called))
        app.exec_()
        self.assertTrue(called[0])

    def test_tk(self):
        try:
            from async_gui.toolkits.tk import TkEngine
            import Tkinter as tk
        except ImportError:
            try:
                import tkinter as tk
            except ImportError:
                return self.skipTest("Tk not installed")

        called = [False]
        root = tk.Tk()
        root.after(0, lambda: self._check_toolkit(TkEngine,
            root, root.quit, called))
        tk.mainloop()
        self.assertTrue(called[0])

    def test_gtk(self):
        try:
            from async_gui.toolkits.pygtk import GtkEngine
            import gtk
        except ImportError:
            return self.skipTest("GTK not installed")
        called = [False]
        gtk.timeout_add(10, lambda: self._check_toolkit(GtkEngine,
                                                  gtk, gtk.main_quit, called))
        gtk.main()
        self.assertTrue(called[0])

    def test_wx(self):
        try:
            from async_gui.toolkits.wx import WxEngine
            import wx
        except ImportError:
            return self.skipTest("WX not installed")
        called = [False]
        app = wx.App(redirect=False)
        frame = wx.Frame(None)
        frame.Show()
        wx.CallLater(50, self._check_toolkit,
                     WxEngine, app, app.ExitMainLoop, called)
        app.MainLoop()
        self.assertTrue(called[0])

    def _check_toolkit(self, engine_class, app, quit_func, called):
        engine = engine_class()
        engine.main_app = app
        N = 10

        def task_func(arg):
            time.sleep(0.2)  # timeout to let update_gui() be called
            return arg

        @engine.async
        def async_gen():
            answer = yield [Task(task_func, i) for i in range(N)]
            self.assertEquals(answer, list(range(N)))
            called[0] = True
            quit_func()

        async_gen()


if __name__ == '__main__':
    unittest.main()
