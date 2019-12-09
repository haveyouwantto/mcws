import asyncio
import glob
import json
import os
import sys
import threading
import time
import math

import mido
import websockets

import drum_set
import instruments_map


def cmd(line):
    return json.dumps({
        "body": {
            "origin": {
                "type": "player"
            },
            "commandLine": line,
            "version": 1
        },
        "header": {
            "requestId": "ffff0000-0000-0000-0000-000000000000",
            "messagePurpose": "commandRequest",
            "version": 1,
            "messageType": "commandRequest"
        }
    })


sub = json.dumps({
    "body": {
        "eventName": "PlayerMessage"
    },
    "header": {
        "requestId": "0ffae098-00ff-ffff-abbb-bbbbbbdf3344",
        "messagePurpose": "subscribe",
        "version": 1,
        "messageType": "commandRequest"
    }
})

helpmsg = {
    '.test': '测试用命令    \u00a7c.test',
    '.help': '提供帮助/命令列表    \u00a7c.help',
    '.play': '播放一个mid文件    \u00a7c.play <ID>',
    '.stop': '停止播放    \u00a7c.stop',
    '.list': '列出mid文件    \u00a7c.list [页码]',
    '.search':'搜索mid文件    \u00a7c.search <内容>'
}

play = True


def getChat(msg):
    return msg["body"]["properties"]["Message"]


def info(msg):
    return cmd("say \u00a7d" + str(msg))


def drawKeyboard(key, start=0):
    out = ""
    i = start
    while i < key:
        if (i % 12 == 1 or i % 12 == 3 or i % 12 == 6 or i % 12 == 8 or i % 12 == 10):
            out += "\u00a70\u258F"
        else:
            out += "\u00a7f\u258F"
        i += 1
    return out


def midiDisplay(midimsg):
    out = '/titleraw @s actionbar {"rawtext":[{"text":"\u00a70'
    i = 0
    out += drawKeyboard(midimsg.note)
    out += "\u00a7c\u258F"
    out += drawKeyboard(128, midimsg.note+1)
    i += 1

    return cmd(out+'"}]}')


def play_note(midimsg, inst):
    origin = midimsg.note - 66
    instrument = instruments_map.inst_map[inst]
    pitch = 2 ** ((origin+instrument[1]) / 12)
    volume = midimsg.velocity / 128
    return cmd("execute @a ~ ~ ~ playsound "+instrument[0]+" @s ^0 ^ ^ " + str(volume) + " " + str(pitch))


def play_perc(midimsg):
    instrument = drum_set.drum_set[midimsg.note]
    pitch = 2 ** (instrument[1] / 12)
    volume = midimsg.velocity / 128
    return cmd("execute @a ~ ~ ~ playsound "+instrument[0]+" @s ^0 ^ ^ " + str(volume) + " " + str(pitch))


def runmain(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value


class midiplayer(threading.Thread):
    def __init__(self, ws):
        threading.Thread.__init__(self)
        self.ws = ws
        self.playing = False
        self.mid = None
        self.setName('Midi Player Thread')
        self.isPlaying = False

    def run(self):
        while True:
            if self.playing:
                inst = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                self.isPlaying = True
                try:
                    for msg in self.mid.play():
                        if msg.type == "note_on" and msg.velocity != 0:
                            if msg.channel != 9:
                                runmain(self.ws.send(
                                    play_note(msg, inst[msg.channel])))
                            else:
                                runmain(self.ws.send(play_perc(msg)))
                        if msg.type == "program_change":
                            inst[msg.channel] = msg.program
                            print(inst)
                        if not self.playing:
                            self.isPlaying = False
                            break
                except Exception as e:
                    runmain(self.ws.send(info(e)))
                    self.mid = None
                    self.playing = False

    def set_midi(self, mid):
        self.mid = mido.MidiFile(mid)

    def play(self):
        self.playing = True

    async def stop(self):
        await self.ws.send(info("正在停止"))
        self.playing = False
        while self.isPlaying:
            pass
        await self.ws.send(info("已停止"))
        return


def setBlock(x, y, z, id, data=0):
    return cmd("setblock " + str(x) + " " + str(y) + " " + str(z) + " " + str(id) + " " + str(data))


def miidDisplay():
    out = '/titleraw @s actionbar {"rawtext":[{"text":"'
    for i in range(128):
        out += "\u258F"
    return out+'"}]}'


def nextItem(_list, start):
    index = start
    while index < len(_list):
        yield _list[index]
        index += 1


async def hello(ws, path):

    player = midiplayer(ws)
    player.start()

    await ws.send(sub)

    sender = "外部"

    #log = open('log.txt', 'a')

    while True:
        data = await ws.recv()
        msg = json.loads(data)
        if msg["header"]["messagePurpose"] == "event":

            if msg["body"]["eventName"] == "PlayerMessage" and msg["body"]["properties"]["Sender"] != sender:

                raw = getChat(msg)

                # log.write(raw+"\n")

                args = raw.split(" ")

                if args[0] == ".test":
                    await ws.send(info("Hello World"))

                if args[0] == ".help":
                    for i in helpmsg:
                        await ws.send(info(i + " - " + helpmsg[i]))

                if args[0] == ".exit":
                    # log.close()
                    sys.exit()

                if args[0] == ".list":
                    try:
                        page = 1
                        if len(args) != 1:
                            page = int(args[1])
                        midils = glob.glob("midis/**/*.mid", recursive=True)
                        iterator = nextItem(midils, (page-1)*10)
                        for i in range(10):
                            num = (page-1)*10+i
                            await ws.send(info('[§c{0}§d] - {1}'.format(num, next(iterator))))
                        await ws.send(info('第 {0} 页，共 {1} 页'.format(page, math.ceil(len(midils)/10))))
                    except StopIteration as e:
                        pass
                    except ValueError as e:
                        await ws.send(info('语法错误'))

                if args[0] == ".stop":
                    await player.stop()

                if args[0] == ".play":
                    try:
                        midils = glob.glob("midis/**/*.mid", recursive=True)
                        arg1 = int(args[1])
                        if arg1 < len(midils):
                            await player.stop()
                            await ws.send(info("正在加载 " + midils[arg1] + "..."))
                            player.set_midi(midils[arg1])
                            player.play()
                            await ws.send(miidDisplay())
                        else:
                            await ws.send(info("文件不存在"))
                    except KeyboardInterrupt:
                        sys.exit()
                    except Exception as e:
                        await ws.send(info(str(e)))

                if args[0] == ".search":
                    midils = glob.glob("midis/**/*.mid", recursive=True)
                    keyword = "".join(args[1:])
                    results = []
                    for i in range(len(midils)):
                        if keyword in midils[i]:
                            results.append((i, midils[i]))
                    for i in results:
                        await ws.send(info('[§c{0}§d] - {1}'.format(i[0], i[1])))

        elif msg["header"]["messagePurpose"] == "commandResponse":
            pass


start_server = websockets.serve(hello, "0.0.0.0", 19111)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
