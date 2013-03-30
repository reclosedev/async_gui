#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "..")
import time

import wx
from async_gui.toolkits.wx import WxEngine
from async_gui.engine import Task, MultiProcessTask

from cpu_work import is_prime, PRIMES


engine = WxEngine()
async = engine.async


class Example(wx.Frame):
  
    def __init__(self, parent, title):
        super(Example, self).__init__(parent, title=title, 
            size=(640, 480))
            
        self.InitUI()
        self.Centre()
        self.Show()     
        
    def InitUI(self):
      
        panel = wx.Panel(self)
        sizer = wx.GridBagSizer(4, 4)

        status = wx.StaticText(panel, label="Status")
        sizer.Add(status, pos=(0, 0),
                  flag=wx.TOP | wx.LEFT | wx.BOTTOM, border=5)
        self.status = status

        button = wx.Button(panel, label="Do work", size=(90, 28))
        button.Bind(wx.EVT_BUTTON, self.cpu_bound)
        sizer.Add(button, pos=(3, 3))

        sizer.AddGrowableCol(1)
        sizer.AddGrowableRow(2)
        panel.SetSizerAndFit(sizer)

    @engine.async
    def cpu_bound(self, event):
        t = time.time()
        self.status.SetLabel("calculating...")
        prime_flags = yield MultiProcessTask(
            [Task(is_prime, n) for n in PRIMES]
        )
        print time.time() - t
        text = '\n'.join("%s: %s" % (n, prime)
        for n, prime in zip(PRIMES, prime_flags))
        self.status.SetLabel(text)
    

if __name__ == '__main__':
    app = wx.App(redirect=False)
    engine.main_app = app
    Example(None, title='Rename')
    app.MainLoop()