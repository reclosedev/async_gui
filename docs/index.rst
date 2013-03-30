.. async_gui documentation master file, created by
   sphinx-quickstart on Sat Mar 30 13:05:39 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to async_gui's documentation!
=====================================

Contents:

.. toctree::
   :maxdepth: 2


Usage
=====

doc TODO:

- engine and toolkits
- tasks in thread, process
- multiple tasks at the same time
- note about processes limitations
- gevent, monkey_patch

Thoughts:

- Do we need optional callbacks? kwargs['callback']?
- Stoping and cancelling loop

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
