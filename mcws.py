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

import_midiplayer = True
import_pixel = True
import_perfinfo=True
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
    
try:
    import perfinfo
except ModuleNotFoundError:
    import_perfinfo = False
    print(ref_strings.import_error.perfinfo)

scoreRegex = r'((- )([\s\S]+?)(: )([-\d]+?)( \()([\s\S][^)]*?)(\)+?))'


def generator(offset=0):
    table = 'abcdefghijklmnopqrstuvwxyz'
    i = offset
    while True:
        i2 = i
        out = ''
        while True:
            out = table[i2 % 26 - 1] + out
            i2 //= 26
            if i2 <= 0:
                break
        yield out
        i += 1


async def hello(ws, path):
    sent = 0
    modules = []
    config = {}
    message_utils.log_command = False

    log = chat_logger.ChatLogger(ws)
    host = await log.getHost()
    modules.append(log)

    we = worldedit.WorldEdit(ws)

    # 加载各模块
    if import_midiplayer:
        player = midiplayer.MidiPlayer(ws)
        player.start()
        modules.append(player)

    if import_pixel:
        pixlegen = pixel.PixelGenerator(ws, we)
        modules.append(pixlegen)

    if import_perfinfo:
        perf = perfinfo.Info()
        perf.start()
        modules.append(perf)

    if os.path.exists('config.json'):
        with open('config.json') as f:
            config = json.loads(f.read())

        for module in modules:
            try:
                module.set_config(config[module.module_id])
            except KeyError:
                module.config = module.default_config
                continue

            for i in module.default_config:
                if i not in module.config:
                    module.config[i] = module.default_config[i]

        message_utils.log_command = config['debug']
    else:
        for module in modules:
            module.config = module.default_config

    print(config)

    # await ws.send(message_utils.info(ref_strings.loading))

    # 监听聊天信息
    await ws.send(message_utils.sub)

    sender = "外部"

    # await ws.send(message_utils.info(ref_strings.mcws.welcome))

    # await ws.send(message_utils.cmd("enableencryption \"MHYwEAYHKoZIzj0CAQYFK4EEACIDYgAEGUO0ZrWHa8kOSIjrrI8Rw8RhYXyM2adkeAyFLNenNEUK16CdJgMjyjxi+zG5hCXZJHmUqRqM4x927duzyzYER/Bdh9Uh9MbN9JX5BeL35IM5YV604nXVslQHXQ3YO1Fb\" \"ml2XwdbswuGmGLLfdd+8Zw==\""))
    # print(await ws.recv())
    # while True:
    #    data=await ws.recv()
    #    print(data)
    def save():

        for i in modules:
            try:
                config[i.module_id] = i.config
            except:
                pass
        config['debug'] = message_utils.log_command
        print(config)
        with open('config.json', 'w') as f:
            f.write(json.dumps(config))
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

                    executor = msg["body"]["properties"]["Sender"]

                    if executor == host:

                        await we.parseCmd(args)

                        if args[0] == ".entitycounter":
                            '''
                            c=entitycounter.EntityCounter(ws)
                            c.start()'''

                        if args[0] == ".getscore":
                            await ws.send(message_utils.cmd("scoreboard players list @s"))
                            msg2 = json.loads(await ws.recv())
                            match = re.findall(scoreRegex, msg2.get(
                                "body").get("statusMessage"))
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
                            pass

                        if args[0] == ".debug":
                            if len(args) == 1:
                                continue
                            if args[1] == '0':
                                message_utils.log_command = False
                            elif args[1] == '1':
                                message_utils.log_command = True

                        if args[0] == '.exit':
                            await ws.send(message_utils.info('bye!'))
                            raise KeyboardInterrupt

                        if args[0] == '.crack':
                            pass
                            '''
                            for i in range(100):
                                cmd = next(a)
                                print(cmd)
                                await ws.send(message_utils.cmd(cmd))
                                data = json.loads(await ws.recv())
                                if data.get('body').get('statusCode') == 0 or data.get('header').get('messagePurpose') != "commandResponse":
                                    found.append(cmd)
                                    print(found)
                                    continue
                                if re.search(findreg, data.get('body').get('statusMessage')) == None:
                                    found.append(cmd)
                                    print(found)
                                    continue

                            offset += 100
                            config['found'] = found
                            config['offset'] = offset
                            
                            with open('config.json', 'w') as f:
                                f.write(json.dumps(config))
                            '''

                        if args[0] == '.copy':
                            origin = worldedit.Position(2, 71, 10)
                            destination = worldedit.Position(-60, 4, -75)
                            for i in range(100):
                                isEnd = await we.isBlock(worldedit.Position(origin.x + i * 2, origin.y-1,
                                                                            origin.z), 'command_block')
                                if isEnd:
                                    break
                                for j in range(4):
                                    for k in range(31):
                                        detectPosition = worldedit.Position(origin.x + i * 2, origin.y + k,
                                                                            origin.z + j * 2)
                                        isBlock = await we.isBlock(detectPosition, 'command_block')
                                        isBlock2 = await we.isBlock(detectPosition, 'chain_command_block')
                                        if isBlock or isBlock2:
                                            await we.copyBlock(detectPosition,
                                                               worldedit.Position(destination.x - (j + i * 4),
                                                                                  destination.y+k,destination.z))
                                        else:
                                            break

                        if args[0] == '.save':
                            save()

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
        save()
        sys.exit()


if __name__ == '__main__':
    start_server = websockets.serve(hello, "0.0.0.0", 26362)
    print('/connect 127.0.0.1:26362')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
