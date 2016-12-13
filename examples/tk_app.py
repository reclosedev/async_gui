import sys
sys.path.insert(0, "..")
try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk
import time

from async_gui.engine import Task, MultiProcessTask
from async_gui.toolkits.tk import TkEngine

from cpu_work import is_prime, PRIMES


engine = TkEngine()


class Application(tk.Frame):
    def __init__(self, master=None):
        tk.Frame.__init__(self, master, width=800, height=400)

        self.grid(sticky=tk.N + tk.S + tk.W + tk.E)
        self.grid_propagate(0)

        self.button = tk.Button(self)
        self.button["text"] = "Check primes"
        self.button["command"] = self.cpu_bound
        self.button.grid(column=0, row=0, sticky=tk.E + tk.W)

        header = tk.Label(self)
        header["text"] = "Status"
        header.grid(column=1, row=0, sticky=tk.W)

        self.status = []
        for i in range(4):
            self.status.append(tk.Label(self))
            self.status[i].grid(column=1, row=1 + i, sticky=tk.W)

    @engine.async
    def cpu_bound(self):
        t = time.time()
        self.status[0]["text"] = "calculating..."
        prime_flags = yield MultiProcessTask(
            [Task(is_prime, n) for n in PRIMES]
        )
        print(time.time() - t)
        text = '\n'.join("%s: %s" % (n, prime)
                         for n, prime in zip(PRIMES, prime_flags))
        self.status[0]["text"] = text


if __name__ == '__main__':
    root = tk.Tk()
    engine.main_app = root
    app = Application(master=root)
    app.mainloop()

