import threading
import time
import message_utils
import json
import tkinter as tk

from mcws_module import BaseModule

import stats
import fileutils

class Info(threading.Thread, BaseModule):
    def __init__(self):
        BaseModule.__init__(self, None)
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.sent = 0
        self.lastSent = stats.commands
        self.lastUpdated = time.time() - 1
        self.speed = 0

    def run(self):
        self.root = tk.Tk()
        self.root.geometry("128x36")

        self.string = tk.StringVar()
        self.string.set('-')
        self.historystring = tk.StringVar()
        self.historystring.set('-')

        self.label = tk.Label(self.root, textvariable=self.string)
        self.label.pack()
        self.historylabel = tk.Label(self.root, textvariable=self.historystring)
        self.historylabel.pack()

        def my_mainloop():
            self.update()
            self.root.after(1000, my_mainloop)

        self.root.after(1000, my_mainloop)
        self.root.mainloop()

    def update(self):
        self.sent = stats.commands - self.lastSent
        t = time.time()
        duration = t - self.lastUpdated
        self.lastUpdated = t
        self.speed = self.sent / duration
        self.lastSent = stats.commands
        self.string.set("{0} | {1}/s".format(message_utils.toSI(self.sent), message_utils.toSI(self.speed)))
        self.historystring.set("{0}".format(message_utils.toSI(self.config['history'])))
