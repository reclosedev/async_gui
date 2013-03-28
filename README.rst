async_gui
---------------

``async_gui`` is a library for make use of threads in GUI applications simpler.
It inspired by PyCon talk
`Using futures for async GUI programming in Python 3.3 <http://pyvideo.org/video/1762/using-futures-for-async-gui-programming-in-python>`_ by
and `tornado <https://github.com/facebook/tornado>`_ ``@gen.engine`` implementation.

Most of GUI toolkits don't allow you to access graphical elements from non-GUI thread.
Python 3.2+ has nice new feature y ``concurrent.futures``, But we can't just
wait for result from future. Callbacks is also not very handy.

Combination of `Coroutines via Enhanced Generators (PEP-342) <http://www.python.org/dev/peps/pep-0342/>`_
and ``futures`` creates a rich and easy to use asynchronous programming model
which can be used for creating highly responsive GUI applications.


Examples
--------

Example of button click handler::

    TBD!!


Examples in example folder (link)!!


Features
--------

- Python 2.7+ (`futures <https://pypi.python.org/pypi/futures>`_ required),
  Python 3+ support

- PyQt4/PySide, Tk, Wx, Gtk? GUI toolkits support. Easy to add another

- Can execute tasks in Thread, Process, Greenlet (`gevent <http://www.gevent.org/>`_ required)

- Possibility to run multiple tasks at the same time

- Straightforward exception handling

- Full test coverage


Links
-----

- TBD!!: **Documentation** at `readthedocs.org <http://readthedocs.org/docs/async_gui/>`_

- **Source code and issue tracking** at `GitHub <https://github.com/reclosedev/async_gui>`_.

