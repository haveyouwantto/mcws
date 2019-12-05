import asyncio
import glob
import json
import os
import threading
import time
import sys

import mido
import websockets


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
    '.function': '运行在相应的功能文件中找到的命令    \u00a7c.function <function>',
    '.midi': '播放一个mid文件    \u00a7c.midi <file>'
}

play = True


def getChat(msg):
    return msg["body"]["properties"]["Message"]


def info(msg):
    return cmd("say \u00a7d" + str(msg))


def play_note(midimsg):
    origin = midimsg.note - 66
    pitch = 2 ** (origin / 12)
    volume = midimsg.velocity / 128
    return cmd("execute @a ~ ~ ~ playsound note.harp @s ^0 ^ ^ " + str(volume) + " " + str(pitch))


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

    def run(self):
        while True:
            if self.playing:
                for msg in self.mid.play():
                    if msg.type == "note_on":
                        print(msg)
                        runmain(self.ws.send(play_note(msg)))
                    if not self.playing:
                        break

    def set_midi(self, mid):
        self.mid = mido.MidiFile(mid)

    def play(self):
        self.playing = True

    def stop(self):
        self.playing = False


def setBlock(x, y, z, id, data=0):
    return cmd("setblock " + str(x) + " " + str(y) + " " + str(z) + " " + str(id) + " " + str(data))


def miidDisplay():
    out = '/titleraw @s actionbar {"rawtext":[{"text":"'
    for i in range(128):
        out += "\u258F"
    return out+'"}]}'


async def hello(ws, path):

    player = midiplayer(ws)
    player.start()

    await ws.send(sub)

    sender = "外部"

    log = open('log.txt', 'a')

    while True:
        data = await ws.recv()
        msg = json.loads(data)
        print(data)
        if msg["header"]["messagePurpose"] == "event":

            if msg["body"]["eventName"] == "PlayerMessage" and msg["body"]["properties"]["Sender"] != sender:

                raw = getChat(msg)

                log.write(raw+"\n")

                args = raw.split(" ")

                if (args[0] == ".test"):
                    await ws.send(info("Hello World"))

                if args[0] == ".help":
                    for i in helpmsg:
                        await ws.send(info(i + " - " + helpmsg[i]))

                if args[0] == ".3nrin2i3nr23i32424i23494":
                    log.close()
                    sys.exit()

                if raw.startswith(".function"):
                    arg1 = raw[10:]
                    if arg1 == "-ls":
                        for filename in glob.glob("functions/*.mcfunction"):
                            await ws.send(info(filename))
                    else:
                        if os.path.exists("functions/" + arg1 + ".mcfunction"):
                            with open("functions/" + arg1 + ".mcfunction", "r") as file:
                                for i in file.readlines():
                                    await ws.send(cmd(i))
                        else:
                            await ws.send(info("文件不存在"))

                if raw.startswith(".midi"):
                    try:
                        midils = glob.glob("midis/*.mid")
                        if args[1] == "-ls":
                            for i in range(len(midils)):
                                await ws.send(info('[§c{0}§d] - {1}'.format(i, midils[i])))
                        elif args[1] == "-stop":
                            player.stop()
                            await ws.send(info("正在停止"))
                        else:
                            arg1 = int(args[1])
                            if arg1 < len(midils):
                                await ws.send(info("正在加载 " + midils[arg1] + "..."))
                                player.stop()
                                player.set_midi(midils[arg1])
                                player.play()
                                await ws.send(miidDisplay())
                                """ 
                                mid = mido.MidiFile(midils[arg1])
                                for msg in mid.play():
                                    if msg.type == "note_on":
                                        print(msg)
                                        await ws.send(play_note(msg)) """
                            else:
                                await ws.send(info("文件不存在"))

                    except Exception as e:
                        await ws.send(info(str(e)))

                if args[0] == ".sier":
                    px = 50200
                    py = 100
                    pz = 50000
                    for x in range(-50, 50):
                        for z in range(-50, 50):
                            y = x ^ z
                            await ws.send(setBlock(px + x, py + y, pz + z, "redstone_block"))
                            time.sleep(0.001)

        elif msg["header"]["messagePurpose"] == "commandResponse":
            pass


start_server = websockets.serve(hello, "0.0.0.0", 19111)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
