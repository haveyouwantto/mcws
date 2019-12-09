import asyncio
import glob
import json
import os
import sys

import websockets

import midiplayer
import chat_logger


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
    '.info': '显示信息    \u00a7c.info',
    '.help': '提供帮助/命令列表    \u00a7c.help',
    '.function': '运行在相应的功能文件中找到的命令    \u00a7c.function <function>',
    '.midi': 'mcws midi 模块    \u00a7c.midi [命令]'
}


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
    out += drawKeyboard(128, midimsg.note + 1)
    i += 1

    return cmd(out + '"}]}')


def runmain(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value


def setBlock(x, y, z, id, data=0):
    return cmd("setblock {0} {1} {2} {3} {4}".format(x, y, z, id, data))


def miidDisplay():
    out = '/titleraw @s actionbar {"rawtext":[{"text":"'
    for i in range(128):
        out += "\u258F"
    return out + '"}]}'


async def hello(ws, path):

    # 加载各模块
    player = midiplayer.MidiPlayer(ws)
    player.start()

    log = chat_logger.ChatLogger(ws)
    await log.getHost()

    await ws.send(info('加载中...'))

    log.authenticate()

    # 监听聊天信息
    await ws.send(sub)

    sender = "外部"

    await ws.send(info('欢迎使用mcws'))

    try:
        while True:
            data = await ws.recv()
            msg = json.loads(data)
            if msg["header"]["messagePurpose"] == "event":

                if msg["body"]["eventName"] == "PlayerMessage" and msg["body"]["properties"]["Sender"] != sender and \
                        msg["body"]["properties"]['MessageType'] == 'chat':

                    log.log(msg)

                    raw = getChat(msg)

                    args = raw.split(" ")

                    if args[0] == ".info":
                        await ws.send(info("\u00a76mcws by HYWT"))

                    if args[0] == ".help":
                        for i in helpmsg:
                            await ws.send(info(i + " - " + helpmsg[i]))

                    if args[0] == ".3nrin2i3nr23i32424i23494":
                        log.close()
                        sys.exit()

                    if args[0] == ".function":
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

                    if args[0] == ".midi":
                        try:
                            await player.parseCmd(args[1:])

                        except Exception as e:
                            await ws.send(info(str(e)))

                    if args[0] == ".sier":
                        pass
                        '''
                        px = 50200
                        py = 100
                        pz = 50000
                        for x in range(-50, 50):
                            for z in range(-50, 50):
                                y = x ^ z
                                await ws.send(setBlock(px + x, py + y, pz + z, "redstone_block"))
                                time.sleep(0.001)'''

            elif msg["header"]["messagePurpose"] == "commandResponse":
                pass
    except (KeyboardInterrupt, websockets.exceptions.ConnectionClosedOK, websockets.exceptions.ConnectionClosedError,
            websockets.exceptions.ConnectionClosed):
        player.close()
        log.close()
        sys.exit()


if __name__ == '__main__':
    start_server = websockets.serve(hello, "0.0.0.0", 19111)
    print('/connect 127.0.0.1:19111')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
