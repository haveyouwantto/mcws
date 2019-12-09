import glob
import math
import threading

import mido

import drum_set
import instruments_map
import mcws


class MidiPlayer(threading.Thread):
    helpmsg = {
        'mcws midi模块': "",
        '-info': '显示信息    \u00a7c-info',
        '-help': '提供帮助/命令列表    \u00a7c-help',
        '-play': '播放一个mid文件    \u00a7c-play <ID>',
        '-stop': '停止播放    \u00a7c-stop',
        '-list': '列出mid文件    \u00a7c-list [页码]',
        '-search': '搜索mid文件    \u00a7c-search <内容>',
        '-reload':'重新加载mid文件列表    \u00a7c-reload'
    }

    def __init__(self, ws):
        threading.Thread.__init__(self)
        self.ws = ws
        self.playing = False
        self.mid = None
        self.setName('Midi Player Thread')
        self.isPlaying = False
        self.midils = glob.glob("midis/**/*.mid", recursive=True)

    async def play_note(self, midimsg, inst):
        origin = midimsg.note - 66
        instrument = instruments_map.inst_map[inst]
        pitch = 2 ** ((origin + instrument[1]) / 12)
        volume = midimsg.velocity / 128
        await self.ws.send(
            mcws.cmd("execute @a ~ ~ ~ playsound " + instrument[0] + " @s ^0 ^ ^ " + str(volume) + " " + str(pitch)))

    async def play_perc(self, midimsg):
        instrument = drum_set.drum_set[midimsg.note]
        pitch = 2 ** (instrument[1] / 12)
        volume = midimsg.velocity / 128
        await self.ws.send(
            mcws.cmd("execute @a ~ ~ ~ playsound " + instrument[0] + " @s ^0 ^ ^ " + str(volume) + " " + str(pitch)))

    def run(self):
        while True:
            if self.playing:
                inst = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                self.isPlaying = True
                try:
                    for msg in self.mid.play():
                        if msg.type == "note_on" and msg.velocity != 0:
                            if msg.channel != 9:
                                mcws.runmain(
                                    self.play_note(msg, inst[msg.channel]))
                            else:
                                mcws.runmain(self.play_perc(msg))
                        if msg.type == "program_change":
                            inst[msg.channel] = msg.program
                            print(inst)
                        if not self.playing:
                            self.isPlaying = False
                            break
                except Exception as e:
                    mcws.runmain(self.ws.send(mcws.info(e)))
                    self.mid = None
                    self.playing = False

    def set_midi(self, mid):
        self.mid = mido.MidiFile(mid)

    def play(self):
        self.playing = True

    async def stop(self):
        await self.ws.send(mcws.info("正在停止"))
        self.playing = False
        while self.isPlaying:
            pass
        await self.ws.send(mcws.info("已停止"))
        return

    async def help(self):
        for i in MidiPlayer.helpmsg:
            await self.ws.send(mcws.info(i + " - " + MidiPlayer.helpmsg[i]))

    async def parseCmd(self, args):

        try:
            if args[0] == "-help":
                await self.help()

            elif args[0] == "-info":
                await self.ws.send(mcws.info("\u00a76mcws midi模块 \u00a7bby HYWT"))

            elif args[0] == "-list":
                try:
                    page = 1
                    if len(args) != 1:
                        page = int(args[1])
                    iterator = nextItem(self.midils, (page - 1) * 10)
                    for i in range(10):
                        num = (page - 1) * 10 + i
                        await self.ws.send(mcws.info('[§c{0}§d] - {1}'.format(num, next(iterator))))
                    await self.ws.send(mcws.info('第 {0} 页，共 {1} 页'.format(page, math.ceil(len(self.midils) / 10))))
                except StopIteration as e:
                    pass
                except ValueError as e:
                    await self.ws.send(mcws.info('页数无效'))

            elif args[0] == "-stop":
                await self.stop()

            elif args[0] == "-play":
                try:
                    arg1 = int(args[1])
                    if arg1 < len(self.midils):
                        await self.stop()
                        await self.ws.send(mcws.info("正在加载 " + self.midils[arg1] + "..."))
                        self.set_midi(self.midils[arg1])
                        self.play()
                    else:
                        await self.ws.send(mcws.info("文件不存在"))
                except ValueError:
                    await self.ws.send(mcws.info('ID 无效'))

            elif args[0] == "-search":
                if args[1:]==[]:
                    await self.ws.send(mcws.info('搜索内容不能为空'))
                    return
                keyword = "".join(args[1:]).lower()
                results = []
                for i in range(len(self.midils)):
                    if keyword in self.midils[i].lower():
                        results.append((i, self.midils[i]))
                if len(results)==0:
                    await self.ws.send(mcws.info('未找到任何结果'))
                for i in results:
                    await self.ws.send(mcws.info('[§c{0}§d] - {1}'.format(i[0], i[1])))
            elif args[0] == "-reload":
                self.midils = glob.glob("midis/**/*.mid", recursive=True)
                await self.ws.send(mcws.info('mid文件列表已重新加载。'))
            else:
                await self.ws.send(mcws.info('未知命令。'))
        except IndexError:
            await self.help()


def nextItem(_list, start):
    index = start
    while index < len(_list):
        yield _list[index]
        index += 1
