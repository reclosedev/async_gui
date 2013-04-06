async_gui
---------------

``async_gui`` is a library aimed to make use of threads in GUI applications simpler.
It's inspired by PyCon talk
`Using futures for async GUI programming in Python 3.3 <http://pyvideo.org/video/1762/using-futures-for-async-gui-programming-in-python>`_
and `tornado <https://github.com/facebook/tornado>`_ ``@gen.engine`` implementation.

Most of GUI toolkits don't allow you to access graphical elements from non-GUI thread.
Python 3.2+ has nice new feature ``concurrent.futures``, but we can't just
wait for result from future and callbacks are not very handy.

Combination of `Coroutines via Enhanced Generators (PEP-342) <http://www.python.org/dev/peps/pep-0342/>`_
and ``futures`` creates a rich and easy to use asynchronous programming model
which can be used for creating highly responsive GUI applications.


Example
-------

Demo of button click handler:

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


Tasks yielded from ``on_button_click()`` executed in thread pool, but
GUI updates done in the GUI thread.
For CPU-bound applications there is also ability to run tasks in pool of
processes.

See `full example <https://github.com/reclosedev/async_gui/blob/master/examples/qt_app.py>`_
in `examples <https://github.com/reclosedev/async_gui/tree/master/examples>`_ directory.


Features
--------

- Python 2.7+ (`futures <https://pypi.python.org/pypi/futures>`_ required),
  Python 3+ support

- PyQt4/PySide, Tk, Wx, Gtk GUI toolkits support. Easy to add another

- Can execute tasks in Thread, Process, Greenlet (`gevent <http://www.gevent.org/>`_ required)

- Possibility to run multiple tasks at the same time

- Straightforward exception handling

- Full test coverage

Installation
------------

Using pip_::

    $ pip install async_gui

Or download, unpack and::

    $ python setup.py install


To run tests use::

    $ python setup.py test

.. _pip: http://www.pip-installer.org/en/latest/installing.html

Links
-----

- **Documentation** at `readthedocs.org <https://async_gui.readthedocs.org/en/latest/>`_

- **Source code and issue tracking** at `GitHub <https://github.com/reclosedev/async_gui>`_.

