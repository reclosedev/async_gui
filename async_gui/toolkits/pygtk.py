#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..engine import Engine
import gtk


class GtkEngine(Engine):
    def update_gui(self):
        if gtk.events_pending():
            gtk.main_iteration()
