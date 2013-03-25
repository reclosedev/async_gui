#!/usr/bin/env python
# -*- coding: utf-8 -*-
from ..engine import Engine, POOL_TIMEOUT


class WxEngine(Engine):
    def __init__(self, pool_timeout=POOL_TIMEOUT):
        super(WxEngine, self).__init__(self._update_gui, pool_timeout)

    def _update_gui(self, timeout=None):
        self.main_app.Yield()

