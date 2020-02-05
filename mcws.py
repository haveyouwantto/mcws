import asyncio
import base64
import glob
import json
import os
import sys
import traceback

import websockets

import chat_logger
import entitycounter
import message_utils
import midiplayer
import ref_strings
import worldedit


def runmain(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value


async def hello(ws, path):
    # 加载各模块
    player = midiplayer.MidiPlayer(ws)
    player.start()

    log = chat_logger.ChatLogger(ws)
    host = await log.getHost()

    we=worldedit.WorldEdit(ws)

    await ws.send(message_utils.info(ref_strings.loading))

    # 监听聊天信息
    await ws.send(message_utils.sub)

    sender = "外部"

    await ws.send(message_utils.info(ref_strings.mcws.welcome))

    # await ws.send(message_utils.cmd("enableencryption \"MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEfHXre8wewVRVY/cCpVP+Rz7ZJg/jxe+ITuhiMeHsr8QdGFzQrn9IU6c3qCdQbi4sf636uIXEwBsQGmgU/JbxO8ugbqMUFswWccPhqpdeCY2CihdHVOsCD1oC9s/hkEnl\" \"7JwjF0k1G1ATc3akeZvgIw==\""))
    # print(await ws.recv())
    # data=await ws.recv()
    # print(base64.b64encode(data))
    try:
        while True:
            data = await ws.recv()
            msg = json.loads(data)
            if msg["header"]["messagePurpose"] == "event":

                if msg["body"]["eventName"] == "PlayerMessage" and msg["body"]["properties"]["Sender"] != sender and \
                        msg["body"]["properties"]['MessageType'] == 'chat':

                    log.log(msg)

                    raw = message_utils.getChat(msg)

                    args = raw.split(" ")

                    if msg["body"]["properties"]["Sender"] == host:

                        await we.parseCmd(args)

                        if args[0] == ".entitycounter":
                            '''
                            c=entitycounter.EntityCounter(ws)
                            c.start()'''

                    if args[0] == ".info":
                        await ws.send(message_utils.info(ref_strings.mcws.info))
                        await ws.send(message_utils.info(ref_strings.pyversion))

                    if args[0] == ".help":
                        for i in ref_strings.mcws.help:
                            await ws.send(message_utils.info(i + " - " + ref_strings.mcws.help[i]))

                    if args[0] == ".function":
                        arg1 = raw[10:]
                        if arg1 == "-ls":
                            for filename in glob.glob("functions/*.mcfunction"):
                                await ws.send(message_utils.info(filename))
                        else:
                            if os.path.exists("functions/" + arg1 + ".mcfunction"):
                                with open("functions/" + arg1 + ".mcfunction", "r") as file:
                                    for i in file.readlines():
                                        await ws.send(message_utils.cmd(i))
                            else:
                                await ws.send(message_utils.error(ref_strings.file_not_exists))

                    if args[0] == ".midi":
                        try:
                            await player.parseCmd(args[1:])

                        except Exception as e:
                            traceback.print_exc()

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
    start_server = websockets.serve(hello, "0.0.0.0", 26362)
    print('/wsserver ws://127.0.0.1:26362')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
