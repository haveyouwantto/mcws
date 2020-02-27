import threading
import time
import message_utils
import tkinter as tk
import json

import stats
import fileutils


class Info(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)

        self.sent = 0
        self.lastUpdated = time.time() - 1
        self.speed = 0

        self.history = 0
        try:
            with open('stats/history.json') as f:
                j = json.loads(f.read())
                self.history = j['history']
        except FileNotFoundError as e:
            pass

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

    def close(self):
        fileutils.mkdirs('stats/')
        with open('stats/history.json', 'w') as f:
            f.write(json.dumps({
                "history": self.history
            }))

    def update(self):
        self.sent += stats.sent
        self.history += stats.sent
        t = time.time()
        duration = t - self.lastUpdated
        self.lastUpdated = t
        self.speed = stats.sent / duration
        self.string.set("{0} | {1}/s".format(message_utils.toSI(self.sent), message_utils.toSI(self.speed)))
        self.historystring.set("{0}".format(message_utils.toSI(self.history)))
        stats.sent = 0
