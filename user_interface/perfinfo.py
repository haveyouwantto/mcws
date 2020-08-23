import threading
import time
from utils import message_utils
import tkinter as tk

from modules.__init__ import BaseModule

from static import stats


class Info(threading.Thread, BaseModule):
    def __init__(self):
        BaseModule.__init__(self, None)
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.sent = 0
        self.lastSent = 0
        self.lastUpdated = time.time() - 1
        self.speed = 0

    def run(self):
        try:
            self.root = tk.Tk()
            self.root.geometry("128x36")

            self.string = tk.StringVar()
            self.string.set('-')

            self.label = tk.Label(self.root, textvariable=self.string)
            self.label.pack()

            def my_mainloop():
                self.update()
                self.root.after(1000, my_mainloop)

            self.root.after(1000, my_mainloop)
            self.root.mainloop()
        except:
            return

    def update(self):
        self.sent = stats.commands - self.lastSent
        t = time.time()
        duration = t - self.lastUpdated
        self.lastUpdated = t
        self.speed = self.sent / duration
        self.lastSent = stats.commands
        self.string.set("{0:08d} | {1}/s".format(stats.commands, message_utils.toSI(self.speed)))
