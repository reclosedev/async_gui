import sys
sys.path.insert(0, "..")
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.gridlayout import GridLayout
import time

from async_gui.engine import Task, MultiProcessTask
from async_gui.toolkits.kivy import KivyEngine

from cpu_work import is_prime, PRIMES


engine = KivyEngine()

class MyApp(App):
    def build(self):
        grid = GridLayout(cols=4)

        grid.add_widget(Button(text='Check Primes',
                               on_press=self.cpu_bound))
        self.status = Label(text='Status')
        grid.add_widget(self.status)
        return grid

    @engine.async
    def cpu_bound(self, *_):
        t = time.time()
        self.status.text = "calculating..."
        prime_flags = yield MultiProcessTask(
            [Task(is_prime, n) for n in PRIMES]
        )
        print(time.time() - t)
        text = '\n'.join("%s: %s" % (n, prime)
                         for n, prime in zip(PRIMES, prime_flags))
        self.status.text = text


if __name__ == '__main__':
    MyApp().run()

