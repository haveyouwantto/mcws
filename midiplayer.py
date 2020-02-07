import math
import threading
import time
import traceback

import mido

import drum_set
import instruments_map
import message_utils
import ref_strings
from mcws_module import Command, FileIOModule


class MidiPlayer(threading.Thread, FileIOModule):

    def __init__(self, ws):
        threading.Thread.__init__(self)
        FileIOModule.__init__(self, ws, 'midis/', ('.mid', '.midi'))
        self.playing = False
        self.mid = None
        self.setName('Midi Player Thread')
        self.setDaemon(True)
        self.isPlaying = False
        self.isClosed = False
        self.searchResult = []
        self.lastQuery = ""
        self.selector = "@a"
        self.add_command(Command('--stop', ('-st',)), self.stop)
        self.add_command(Command('--play', ('-p',)), self.open_file)

    async def play_note(self, midimsg, inst, pan, chanvol):
        origin = midimsg.note - 66
        instrument = instruments_map.inst_map[inst]
        pitch = 2 ** ((origin + instrument[1]) / 12)
        volume = midimsg.velocity / 127 * chanvol
        await self.ws.send(
            message_utils.cmd(
                "execute " + self.selector + " ~ ~ ~ playsound " + instrument[0] + " @s ^" + str(
                    math.asin(pan * 2) * -2.5464790894703255) + " ^ ^ " + str(
                    volume) + " " + str(pitch)))

    async def play_perc(self, midimsg, pan, chanvol):
        instrument = drum_set.drum_set[midimsg.note]
        pitch = 2 ** (instrument[1] / 12)
        volume = midimsg.velocity / 127 * chanvol
        await self.ws.send(
            message_utils.cmd(
                "execute " + self.selector + " ~ ~ ~ playsound " + instrument[0] + " @s ^" + str(
                    math.asin(pan * 2) * -2.5464790894703255) + " ^ ^ " + str(
                    volume) + " " + str(pitch)))

    def run(self):
        while True:
            if self.playing:
                inst = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                pan = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                channel_volume = [1, 1, 1, 1, 1, 1,
                                  1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
                self.isPlaying = True
                try:
                    for msg in self.mid.play():
                        if not self.playing:
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

                except Exception as e:
                    traceback.print_exc()
                    message_utils.runmain(self.ws.send(message_utils.info(e)))
                    self.mid = None
                    self.isPlaying = False
                    self.playing = False
            else:
                time.sleep(0.05)

    async def set_midi(self, mid):
        try:
            self.mid = mido.MidiFile(mid)
        except Exception as e:
            await self.ws.send(message_utils.error(e))

    async def open(self, filename):
        await self.stop()
        await self.ws.send(
            message_utils.info(ref_strings.midiplayer.load_song.format(filename)))
        await self.set_midi(filename)
        self.play()

    def play(self):
        self.playing = True

    async def stop(self):
        await self.ws.send(message_utils.info(ref_strings.midiplayer.stopping))
        self.playing = False
        while self.isPlaying:
            time.sleep(0.05)
        await self.ws.send(message_utils.info(ref_strings.midiplayer.stopped))
        return

    async def help(self,args):
        for i in ref_strings.midiplayer.help:
            await self.ws.send(message_utils.info(i + " , " + ref_strings.midiplayer.help[i]))

    async def info(self, args):
        await self.ws.send(message_utils.info(ref_strings.midiplayer.info))
        await self.ws.send(message_utils.info(ref_strings.midiplayer.midicount.format(len(self.file_list))))

    def close(self):
        self.isClosed = True
