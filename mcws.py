import asyncio
import glob
import json
import os
import sys
import traceback
import re

import websockets

import message_utils
import ref_strings

import chat_logger
import worldedit
import mcws_module
import perfinfo

import_midiplayer = True
import_pixel = True
try:
    import midiplayer
except ModuleNotFoundError:
    import_midiplayer = False
    print(ref_strings.import_error.midiplayer)
try:
    import pixel
except ModuleNotFoundError:
    import_pixel = False
    print(ref_strings.import_error.pixel)

scoreRegex = r'((- )([\s\S]+?)(: )([-\d]+?)( \()([\s\S][^)]*?)(\)+?))'

debug=False

async def hello(ws, path):

    sent = 0

    perf = perfinfo.Info()
    perf.start()

    # 加载各模块
    if import_midiplayer:
        player = midiplayer.MidiPlayer(ws)
        player.start()

    log = chat_logger.ChatLogger(ws)
    host = await log.getHost()

    we = worldedit.WorldEdit(ws)

    if import_pixel:
        pixlegen = pixel.PixelGenerator(ws, we)

    await ws.send(message_utils.info(ref_strings.loading))

    # 监听聊天信息
    await ws.send(message_utils.sub)

    sender = "外部"

    await ws.send(message_utils.info(ref_strings.mcws.welcome))

    mod = mcws_module.FileIOModule(ws, 'midis/', ('.mid', '.midi'))

    # await ws.send(message_utils.cmd("enableencryption \"MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEfHXre8wewVRVY/cCpVP+Rz7ZJg/jxe+ITuhiMeHsr8QdGFzQrn9IU6c3qCdQbi4sf636uIXEwBsQGmgU/JbxO8ugbqMUFswWccPhqpdeCY2CihdHVOsCD1oC9s/hkEnl\" \"7JwjF0k1G1ATc3akeZvgIw==\""))
    # print(await ws.recv())
    # data=await ws.recv()
    # print(base64.b64encode(data))
    try:
        while True:
            data = await ws.recv()
            msg = json.loads(data)
            sent += 1
            sent = 0
            if msg["header"]["messagePurpose"] == "event":

                if msg["body"]["eventName"] == "PlayerMessage" and msg["body"]["properties"]["Sender"] != sender and \
                        msg["body"]["properties"]['MessageType'] == 'chat':

                    log.log(msg)

                    raw = message_utils.getChat(msg)

                    args = raw.split(" ")

                    executor=msg["body"]["properties"]["Sender"]

                    if executor == host:

                        await we.parseCmd(args)

                        if args[0] == ".entitycounter":
                            '''
                            c=entitycounter.EntityCounter(ws)
                            c.start()'''

                        if args[0] == ".getscore":
                            await ws.send(message_utils.cmd("scoreboard players list @s"))
                            msg2 = json.loads(await ws.recv())
                            match = re.findall(scoreRegex, msg2.get("body").get("statusMessage"))
                            out = {}
                            for i in match:
                                out[i[2]] = i[4]
                            print(out)

                        if args[0] == ".pixelart" and import_pixel:
                            try:
                                await pixlegen.parse_command(args[1:])
                            except FileNotFoundError:
                                await ws.send(message_utils.error(ref_strings.file_not_exists))

                        if args[0] == ".test":
                            await mod.parse_command('--search touhou')

                        if args[0] == '.exit':
                            await ws.send(message_utils.info('bye!'))
                            raise KeyboardInterrupt

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

                    if args[0] == ".midi" and import_midiplayer:
                        try:
                            await player.parse_command(args[1:])

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
        perf.close()
        sys.exit()


if __name__ == '__main__':
    start_server = websockets.serve(hello, "0.0.0.0", 26362)
    print('/connect 127.0.0.1:26362')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
