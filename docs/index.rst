.. async_gui documentation master file, created by
   sphinx-quickstart on Sat Mar 30 13:05:39 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

async_gui's documentation
=========================

.. toctree::
   :maxdepth: 2


Usage
=====

Installation
------------

Install with pip_ or easy_install_::

    $ pip install --upgrade async_gui

or download latest version from GitHub::

    $ git clone https://github.com/reclosedev/async_gui.git
    $ cd async_gui
    $ python setup.py install

To run tests::

    $ python setup.py test


.. _pip: http://www.pip-installer.org/en/latest/installing.html
.. _easy_install: https://pypi.python.org/pypi/distribute#installation-instructions


First steps
-----------
.. currentmodule:: async_gui.engine

First create :class:`Engine` instance corresponding to your GUI toolkit (see
:ref:`supported-gui-toolkits`):

.. code-block:: python

    from async_gui.tasks import Task
    from async_gui.toolkits.pyqt import PyQtEngine

    engine = PyQtEngine()

It contains decorator :meth:`@engine.async <Engine.async>` which allows you to
write asynchronous code in serial way without callbacks.
Example button click handler:

.. code-block:: python

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

Before starting GUI mainloop set :attr:`Engine.main_app` property, so it can
update GUI while executing tasks::

    app = QtGui.QApplication(sys.argv)
    engine.main_app = app
    ...
    sys.exit(app.exec_())

.. note:: It's not necessarily for PyQT4/PySide and Gtk.

Tasks in threads
----------------
.. currentmodule:: async_gui.tasks

Tasks yielded from generator (``on_button_click()``) executed in thread pool, but
GUI updates done in the GUI thread.

If exception occur during execution of task callable, it will be thrown in
GUI thread and can be catched:

.. code-block:: python

    try:
        result = yield Task(func_that_may_raise_exception)
    except SomeException as e:
        # show message, log it, etc...

If generator yields list of :class:`Task`, they
are executed simultaneously. If you want to control number of
simultaneous tasks use :class:`async_gui.tasks.MultiTask`.
Example with 4 workers:

.. code-block:: python

    from async_gui.tasks import MultiTask
    ...
    results = yield MultiTask([Task(do_something, i) for i in range(10)],
                              max_workers=4)


If one of the tasks raises exception then it will be raised in GUI thread
and results will not be returned.
To skip errors use ``skip_errors=True`` argument
for :class:`async_gui.tasks.MultiTask`. Only successful results will be returned

.. code-block:: python

    results = yield MultiTask([Task(do_something, i) for i in range(10)],
                              skip_errors=True)


Tasks in processes
------------------

For CPU-bound applications you can use ability to run tasks in pool of
processes. Just change :class:`Task` to :class:`ProcessTask`

.. code-block:: python

    from async_gui.tasks import ProcessTask
    ...
    result = yield ProcessTask(function_for_process)

.. note::  ``function_for_process`` should be importable.
           Also see `multiprocessing documentation <http://docs.python.org/library/multiprocessing.html>`_
           for limitations and Programming guidelines.

If generator yields list of :class:`ProcessTask`, they are executed in
pool of processes. Default number of simultaneous tasks equals to number of
CPU cores. If you want to control number of simultaneous tasks use
:class:`async_gui.tasks.MultiProcessTask`.

See `full example <https://github.com/reclosedev/async_gui/blob/master/examples/qt_app.py>`_ in `examples` directory.
There is also examples of Tkinter, Gtk and WxPython applications.


Tasks in greenlets
------------------
.. currentmodule:: async_gui.gevent_tasks

You can also run tasks in `gevent <http://www.gevent.org/>`_  greenlets.
See :class:`GTask` and :class:`MultiGTask`

.. note:: You need to apply gevent monkey-patch yourself, see
      `Gevent docs <http://www.gevent.org/gevent.monkey.html>`_


Returning result
----------------
.. currentmodule:: async_gui.engine

In Python < 3.3 you can't return result from generator. But if you need to,
you can use :func:`return_result` function which is
shortcut for raising :class:`ReturnResult` exception.


.. _supported-gui-toolkits:

Supported GUI toolkits
======================

Currently supported gui toolkits:

=========   =============================================
Toolkit     Engine class
=========   =============================================
PyQt4       :class:`async_gui.toolkits.pyqt.PyQtEngine`

PySide      :class:`async_gui.toolkits.pyside.PySideEngine`

Tkinter     :class:`async_gui.toolkits.tk.TkEngine`

WxPython    :class:`async_gui.toolkits.wx.WxEngine`

GTK         :class:`async_gui.toolkits.pygtk.GtkEngine`
=========   =============================================

.. currentmodule:: async_gui.engine

You can simply add support for another toolkit by subclassing
:class:`async_gui.engine.Engine` and overriding :meth:`Engine.update_gui`

For more information see :ref:`api-docs`,
`examples <https://github.com/reclosedev/async_gui/tree/master/examples>`_,
sources and tests.

.. _api-docs:

API
===

.. automodule:: async_gui.engine
    :members:

.. automodule:: async_gui.tasks
    :members:

.. automodule:: async_gui.gevent_tasks

    .. autoclass:: GTask
    .. autoclass:: MultiGTask


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
