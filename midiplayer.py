import math
import threading
import time

import mido

import drum_set
import instruments_map
import message_utils
import ref_strings
from mcws_module import Command, FileIOModule
import downloader


class MidiPlayer(threading.Thread, FileIOModule):

    def __init__(self, ws):
        threading.Thread.__init__(self)
        FileIOModule.__init__(self, ws, 'midis/', ('.mid', '.midi'), ref_strings.midiplayer.name,
                              ref_strings.midiplayer.description)
        self.playing = False
        self.mid = None
        self.setName('Midi Player Thread')
        self.setDaemon(True)
        self.isPlaying = False
        self.isClosed = False
        self.searchResult = []
        self.lastQuery = ""
        self.selector = "@a"
        self.commands['--list']['command'].description = ref_strings.midiplayer.help['--list']
        self.commands['--search']['command'].description = ref_strings.midiplayer.help['--search']
        self.commands['--reload']['command'].description = ref_strings.midiplayer.help['--reload']
        self.add_command(Command('--stop', ('-st',), ref_strings.midiplayer.help['--stop']), self.stop)
        self.add_command(Command('--play', ('-p',), ref_strings.midiplayer.help['--play']), self.open_file)
        self.add_command(Command('--from-url', ('-u',), ref_strings.midiplayer.help['--from-url']), self.from_url)

    async def from_url(self, args):
        await self.ws.send(message_utils.info(ref_strings.pixel.download_image.format(args[0])))
        if len(args) == 0:
            return
        code = downloader.download_midi(args[0])
        if code[0] == -1:
            await self.ws.send(message_utils.error(ref_strings.pixel.web_error.format(args[0])))
            return
        if code[0] == 1:
            await self.ws.send(message_utils.error(ref_strings.pixel.mime_error.format(code[1])))
            return
        await self.open('cache/midi')

    async def play_note(self, midimsg, inst, pan, chanvol):
        origin = midimsg.note - 66
        instrument = instruments_map.inst_map[inst]
        pitch = math.pow(2, ((origin + instrument[1]) / 12))
        volume = math.pow(midimsg.velocity / 127 * chanvol, 2)
        await self.ws.send(
            message_utils.cmd("execute {0} ~ ~ ~ playsound {1} @s ^{2:.4n} ^ ^ {3:.4n} {4:.4n}".format(
                self.selector,
                instrument[0],
                math.asin(pan * 2) * -2.5464790894703255,
                volume,
                pitch
            ))
        )

    async def play_perc(self, midimsg, pan, chanvol):
        instrument = drum_set.drum_set[midimsg.note]
        pitch = math.pow(2, (instrument[1] / 12))
        volume = math.pow(midimsg.velocity / 127 * chanvol, 2)
        await self.ws.send(
            message_utils.cmd("execute {0} ~ ~ ~ playsound {1} @s ^{2:.4n} ^ ^ {3:.4n} {4:.4n}".format(
                self.selector,
                instrument[0],
                math.asin(pan * 2) * -2.5464790894703255,
                volume,
                pitch
            ))
        )

    def run(self):
        while True:
            if self.playing:
                inst = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                pan = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                channel_volume = [1, 1, 1, 1, 1, 1,
                                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                self.isPlaying = True
                for msg in self.mid.play():
                    if (not self.playing) or self.isClosed:
                        self.isPlaying = False
                        break
                    if msg.type == "note_on" and msg.velocity != 0:
                        if msg.channel != 9:
                            message_utils.runmain(
                                self.play_note(msg, inst[msg.channel], pan[msg.channel],
                                               channel_volume[msg.channel]))
                        else:
                            message_utils.runmain(self.play_perc(
                                msg, pan[msg.channel], channel_volume[msg.channel]))
                    elif msg.type == "program_change":
                        inst[msg.channel] = msg.program
                    elif msg.type == "control_change":
                        if msg.control == 10:
                            pan[msg.channel] = msg.value / 127 - 0.5
                        elif msg.control == 7:
                            channel_volume[msg.channel] = msg.value / 127
            else:
                time.sleep(0.05)

    async def set_midi(self, mid):
        self.mid = mido.MidiFile(mid)

    async def open(self, filename):
        if self.playing:
            await self.stop()
        await self.ws.send(
            message_utils.info(ref_strings.midiplayer.load_song.format(filename, message_utils.filesize(filename))))
        await self.set_midi(filename)
        self.play()

    def play(self):
        self.playing = True

    async def stop(self, args=None):
        await self.ws.send(message_utils.info(ref_strings.midiplayer.stopping))
        self.playing = False
        while self.isPlaying:
            time.sleep(0.05)
        await self.ws.send(message_utils.info(ref_strings.midiplayer.stopped))
        return

    '''
    async def help(self, args):
        for i in ref_strings.midiplayer.help:
            await self.ws.send(message_utils.info(i + " , " + ref_strings.midiplayer.help[i]))
    '''

    async def info(self, args):
        await self.ws.send(message_utils.info(ref_strings.midiplayer.info))
        await self.ws.send(message_utils.info(ref_strings.midiplayer.midicount.format(len(self.file_list))))

    def close(self):
        self.isClosed = True
