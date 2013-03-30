#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "..")
import time

import pygtk
pygtk.require('2.0')
import gtk

from async_gui import MultiProcessTask, Task
from async_gui.toolkits.pygtk import GtkEngine
from examples.cpu_work import is_prime, PRIMES

engine = GtkEngine()


class GtkExample:
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.connect("destroy", self.destroy)
        box = gtk.VBox()
        self.button = gtk.Button("Check primes")
        self.button.connect("clicked", self.check_primes, None)
        self.status = gtk.Label("Ready")
        self.window.add(box)
        box.add(self.button)
        box.add(self.status)

        self.status.show()
        self.button.show()
        box.show()
        self.window.show()

    @engine.async
    def check_primes(self, widget, data=None):
        t = time.time()
        self.status.set_label("Checking primes...")
        prime_flags = yield MultiProcessTask(
            [Task(is_prime, n) for n in PRIMES]
        )
        elapsed = "Elapsed: %.3f seconds\n" % (time.time() - t)
        text = '\n'.join("%s: %s" % (n, prime)
                         for n, prime in zip(PRIMES, prime_flags))
        self.status.set_label(elapsed + text)

    def destroy(self, widget, data=None):
        gtk.main_quit()

    def main(self):
        gtk.main()


if __name__ == "__main__":
    hello = GtkExample()
    hello.main()
