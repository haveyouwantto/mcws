import json
import threading
import time

import matplotlib.pyplot as plt

import mcws
import message_utils


class EntityCounter(threading.Thread):
    def __init__(self, ws):
        threading.Thread.__init__(self)
        self.ws = ws
        self.setName('Entity Counter Thread')
        self.setDaemon(True)
        plt.ion()  # 开启interactive mode 成功的关键函数
        plt.figure(1)
        self.start_time = time.time()
        self.time = []
        self.count = []

    def run(self):
        while True:
            self.update()
            
    async def update(self):
        await self.ws.send(message_utils.cmd('testfor @e'))
        data = json.loads(await self.ws.recv())
        if not 'victim' in data['body']:
            self.time.append(
            time.time()-self.start_time)
            self.count.append(0)
            plt.plot(self.time, self.count, 'r')
            plt.pause(1)
            return
        self.time.append(
            time.time()-self.start_time)
        self.count.append(len(data['body']['victim']))
        plt.plot(self.time, self.count, 'r')
        if len(self.time>60):
            self.time.pop(0)
            self.count.pop(0)
        plt.pause(1)
