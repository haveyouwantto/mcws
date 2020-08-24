import asyncio
import glob
import json
import os
import re
import sys
import traceback
import _thread

import websockets

import worldedit
from modules import chat_logger
from static import stats, ref_strings
from utils import message_utils, uuidgen

scoreRegex = r'((- )([\s\S]+?)(: )([-\d]+?)( \()([\s\S][^)]*?)(\)+?))'

import_midiplayer = True
import_pixel = True
import_perfinfo = True
import_webui = True

try:
    from modules import midiplayer
except ModuleNotFoundError:
    import_midiplayer = False
    print(ref_strings.import_error.midiplayer)
try:
    from modules import pixel
except ModuleNotFoundError:
    import_pixel = False
    print(ref_strings.import_error.pixel)

try:
    from user_interface import webui
except ModuleNotFoundError:
    import_webui = False
    print(ref_strings.import_error.webui)


class MCWS:

    async def start(self, ws, path):
        self.ws = ws
        self.modules = {}
        self.config = {'stats': {},'modules':{}}
        message_utils.log_command = False

        await self.load_modules()
        await self.load_config()
        await self.listen_event()
        await self.hello()

    async def load_modules(self):

        log = chat_logger.ChatLogger(self.ws)
        await log.getHost()
        self.modules[log.module_id] = log

        self.we = worldedit.WorldEdit(self.ws)

        # 加载各模块
        if import_midiplayer:
            player = midiplayer.MidiPlayer(self.ws)
            player.start()
            self.modules[player.module_id] = player

        if import_pixel:
            pixlegen = pixel.PixelArtGenerator(self.ws, self.we)
            self.modules[pixlegen.module_id] = pixlegen

        if import_webui:
            def s():
                webui.app.run(port=26363, threaded=True)

            webui.wsserver = self
            _thread.start_new_thread(s, ())
            print(ref_strings.webui)

    async def load_config(self):
        if os.path.exists('files/config.json'):
            with open('files/config.json') as f:
                self.config = json.loads(f.read())

            for key in self.modules:
                module = self.modules[key]
                try:
                    module.set_config(self.config['modules'][module.module_id])
                except KeyError:
                    module.config = module.default_config
                    continue

                for i in module.default_config:
                    if i not in module.config:
                        module.config[i] = module.default_config[i]

            message_utils.log_command = self.config['debug']
            stats.commands = self.config['stats']['commands']
            uuidgen.id = self.config['stats']['commands']
        else:
            for module in self.modules:
                module.config = module.default_config

        print(self.config)

    async def listen_event(self):
        # 监听聊天信息
        await self.ws.send(message_utils.sub)
        self.sender = "外部"  # TODO detect ws name

    def get_config(self):
        for k in self.modules:
            module = self.modules[k]
            try:
                self.config['modules'][module.module_id] = module.config
            except:
                pass
        self.config['debug'] = message_utils.log_command
        self.config['stats']['commands'] = stats.commands
        return self.config

    def save(self):
        self.get_config()
        print(self.config)
        with open('files/config.json', 'w') as f:
            f.write(json.dumps(self.config))

    async def hello(self):
        # await ws.send(message_utils.info(ref_strings.loading))
        log = self.modules['ChatLogger']
        player = self.modules['MidiPlayer']
        pixelgen = self.modules['PixelArtGenerator']
        try:
            while True:
                data = await self.ws.recv()
                msg = json.loads(data)
                if msg["header"]["messagePurpose"] == "event":

                    if msg["body"]["eventName"] == "PlayerMessage" and msg["body"]["properties"][
                        "Sender"] != self.sender and \
                            msg["body"]["properties"]['MessageType'] == 'chat':

                        log.log(msg)

                        raw = message_utils.getChat(msg)

                        args = raw.split(" ")

                        executor = msg["body"]["properties"]["Sender"]

                        if executor == log.host:

                            await self.we.parseCmd(args)

                            if args[0] == ".entitycounter":
                                '''
                                c=entitycounter.EntityCounter(ws)
                                c.start()'''

                            if args[0] == ".getscore":
                                await self.ws.send(message_utils.autocmd("scoreboard players list @s"))
                                msg2 = json.loads(await self.ws.recv())
                                match = re.findall(scoreRegex, msg2.get(
                                    "body").get("statusMessage"))
                                out = {}
                                for i in match:
                                    out[i[2]] = i[4]
                                print(out)

                            if args[0] == ".pixelart" and import_pixel:
                                try:
                                    await pixelgen.parse_command(args[1:])
                                except FileNotFoundError:
                                    await self.ws.send(message_utils.error(ref_strings.file_not_exists))

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
                                await self.ws.send(message_utils.info('bye!'))
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
                                    isEnd = await self.we.isBlock(worldedit.Position(origin.x + i * 2, origin.y - 1,
                                                                                     origin.z), 'command_block')
                                    if isEnd:
                                        break
                                    for j in range(4):
                                        for k in range(31):
                                            detectPosition = worldedit.Position(origin.x + i * 2, origin.y + k,
                                                                                origin.z + j * 2)
                                            isBlock = await self.we.isBlock(detectPosition, 'command_block')
                                            isBlock2 = await self.we.isBlock(detectPosition, 'chain_command_block')
                                            if isBlock or isBlock2:
                                                await self.we.copyBlock(detectPosition,
                                                                        worldedit.Position(destination.x - (j + i * 4),
                                                                                           destination.y + k,
                                                                                           destination.z))
                                            else:
                                                break

                            if args[0] == '.save':
                                self.save()

                        if args[0] == ".info":
                            await self.ws.send(message_utils.info(ref_strings.mcws.info))
                            await self.ws.send(message_utils.info(ref_strings.pyversion))

                        if args[0] == ".help":
                            for i in ref_strings.mcws.help:
                                await self.ws.send(message_utils.info(i + " - " + ref_strings.mcws.help[i]))

                        if args[0] == ".function":
                            arg1 = raw[10:]
                            if arg1 == "-ls":
                                for filename in glob.glob("files/functions/*.mcfunction"):
                                    await self.ws.send(message_utils.info(filename))
                            else:
                                if os.path.exists("functions/" + arg1 + ".mcfunction"):
                                    with open("functions/" + arg1 + ".mcfunction", "r") as file:
                                        for i in file.readlines():
                                            await self.ws.send(message_utils.autocmd(i))
                                else:
                                    await self.ws.send(message_utils.error(ref_strings.file_not_exists))

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

        except (
                KeyboardInterrupt, websockets.exceptions.ConnectionClosedOK,
                websockets.exceptions.ConnectionClosedError,
                websockets.exceptions.ConnectionClosed):
            player.close()
            log.close()
            self.save()
            sys.exit()


if __name__ == '__main__':
    server = MCWS()
    start_server = websockets.serve(server.start, "0.0.0.0", 26362)
    print('/connect 127.0.0.1:26362')

    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
