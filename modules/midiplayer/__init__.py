import math
import threading
import time

import mido
import numpy as np

from modules.midiplayer import instruments_map, drum_set, mcsparser
from static import ref_strings
from modules.__init__ import Command, FileIOModule
from utils import downloader, message_utils

palette = 'ca1edb62574398ff'

insts = [
    'note.harp',
    'note.bass',
    'note.bd',
    'note.snare',
    'note.hat',
    'note.guitar',
    'note.flute',
    'note.bell',
    'note.chime',
    'note.xylophone',
    'note.iron_xylophone',
    'note.cowbell',
    'note.didgeridoo',
    'note.bit',
    'note.banjo',
    'note.pling'
]
offsets = {
    'note.harp': 0,
    'note.bass': -2,
    'note.bd': -2,
    'note.snare': -2,
    'note.hat': -2,
    'note.guitar': -1,
    'note.flute': +1,
    'note.bell': +2,
    'note.chime': +3,
    'note.xylophone': +2,
    'note.iron_xylophone': 0,
    'note.cowbell': 0,
    'note.didgeridoo': -2,
    'note.bit': 0,
    'note.banjo': 0,
    'note.pling': 0
}


def isBlackKey(i):
    if i % 12 == 1 or i % 12 == 3 or i % 12 == 6 or i % 12 == 8 or i % 12 == 10:
        return True
    else:
        return False


class KeyBoard:
    def __init__(self):
        self.keys = []
        self.colorMode = 0
        self.reset()

    def reset(self):
        for i in range(128):
            self.keys.append([])

    def add(self, note):
        self.keys[note['note']].append(note)

    def remove(self, note):
        self.keys[note['note']].remove(note)

    def __str__(self):
        out = '\u00a70'
        for i in range(128):
            if self.keys[i]:
                for j in self.keys[i]:
                    out += '\u00a7' + palette[j['channel']]
            """
            else:
                if isBlackKey(i):
                    out+='\u00a70'
                else:
                    out+='\u00a7f'
            """
            out += '\u258F'
            if self.keys[i]:
                out += '\u00a70'
        return out


class MidiPlayer(threading.Thread, FileIOModule):

    def __init__(self, ws):
        threading.Thread.__init__(self)
        FileIOModule.__init__(self, ws, 'files/midis/', ('.mid', '.midi', '.mcs', '.mcz'), ref_strings.midiplayer.name,
                              ref_strings.midiplayer.description)
        self.playing = False
        self.mid = None
        self.setName('Midi Player Thread')
        self.setDaemon(True)
        self.isPlaying = False
        self.isClosed = False
        self.keyboard = KeyBoard()
        self.searchResult = []
        self.lastQuery = ""
        self.selector = "@a"
        self.mcsMode = False
        self.mcs = None

        self.commands['--list']['command'].description = ref_strings.midiplayer.help['--list']
        self.commands['--search']['command'].description = ref_strings.midiplayer.help['--search']
        self.commands['--reload']['command'].description = ref_strings.midiplayer.help['--reload']

        self.add_command(Command('--stop', ('-st', 'stop'),
                                 ref_strings.midiplayer.help['--stop']), self.stop)
        self.add_command(Command('--play', ('-p', 'play'),
                                 ref_strings.midiplayer.help['--play']), self.open_file)
        self.add_command(Command('--from-url', ('-u',),
                                 ref_strings.midiplayer.help['--from-url']), self.from_url)
        self.add_command(Command('--keyboard', ('-k', 'keyboard'),
                                 ref_strings.midiplayer.help['--keyboard']), self.set_keyboard)
        self.add_command(Command('--pan-by-pitch', ('-pp',), ref_strings.midiplayer.help['--pan-by-pitch']),
                         self.set_pan_by_pitch)
        self.add_command(Command('--playing', ('-pl', 'playing'),
                                 ref_strings.midiplayer.help['--playing']), self.show_playing)
        self.add_command(Command('--loop', ('-l', 'loop'),
                                 ref_strings.midiplayer.help['--loop']), self.set_loop)

        self.default_config = {
            'displayKeyboard': False,
            'panByPitch': False,
            'loop': 'song'
        }

    async def set_keyboard(self, args):
        if len(args) == 0:
            return
        if args[0] == '0':
            self.config['displayKeyboard'] = False
            await self.ws.send(message_utils.info(ref_strings.midiplayer.keyboard_disable))
        elif args[0] == '1':
            self.config['displayKeyboard'] = True
            await self.ws.send(message_utils.info(ref_strings.midiplayer.keyboard_enable))

    async def set_pan_by_pitch(self, args):
        if len(args) == 0:
            return
        if args[0] == '0':
            self.config['panByPitch'] = False
            await self.ws.send(message_utils.info(ref_strings.midiplayer.by_pitch_disable))
        else:
            self.config['panByPitch'] = True
            await self.ws.send(message_utils.info(ref_strings.midiplayer.by_pitch_enable))

    async def set_loop(self, args):
        if len(args) == 0:
            return
        if args[0] == 'song':
            self.config['loop'] = 'song'
        elif args[0] == 'all':
            self.config['loop'] = 'all'

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
        await self.open('files/cache/midi')

    async def show_playing(self, args):
        if self.playing:
            await self.ws.send(
                message_utils.info(ref_strings.midiplayer.playing.format(self.index, self.file_list[self.index])))

    async def play_note(self, midimsg, inst, pan, chanvol):
        origin = midimsg.note - 66
        instrument = instruments_map.inst_map[inst]
        pitch = math.pow(2, ((origin + instrument[1]) / 12))
        volume = math.pow(midimsg.velocity / 127 * chanvol, 2)
        if self.config['panByPitch']:
            pan = midimsg.note / 127 - 0.5
        await self.playsound(
            self.selector,
            instrument[0],
            math.asin(pan * 2) * -2.5464790894703255,
            volume,
            pitch
        )

    async def play_inst(self, note, inst, velocity, pan):
        origin = note - 66
        pitch = math.pow(2, (origin / 12))
        volume = math.pow(velocity / 127, 2)
        if self.config['panByPitch']:
            pan = note / 127 - 0.5
        await self.playsound(
            self.selector,
            inst,
            math.asin(pan * 2) * -2.5464790894703255,
            volume,
            pitch
        )

    async def play_perc(self, midimsg, pan, chanvol):
        instrument = drum_set.drum_set[midimsg.note]
        pitch = math.pow(2, (instrument[1] / 12))
        volume = math.pow(midimsg.velocity / 127 * chanvol, 2)
        await self.playsound(
            self.selector, instrument[0],
            math.asin(pan * 2) * -2.5464790894703255,
            volume,
            pitch
        )

    async def playsound(self, selector, sound, pan, volume, pitch):
        await self.ws.send(
            message_utils.autocmd("execute {0} ~ ~ ~ playsound {1} @s ^{2} ^ ^ {3} {4}".format(
                selector,
                sound,
                message_utils.formatNumber(pan),
                message_utils.formatNumber(volume),
                message_utils.formatNumber(pitch)
            ))
        )

    async def updatekey(self):
        await self.ws.send(message_utils.autocmd('title {0} actionbar {1}'.format(self.selector, self.keyboard)))

    def run(self):
        while True:
            if self.playing:
                inst = np.zeros(16, dtype='uint8')
                pan = np.zeros(16, dtype='uint8')
                channel_volume = np.ones(16)
                self.isPlaying = True
                try:
                    if self.mcsMode:
                        if self.mcs['version'] == 0:
                            for note in self.mcs['notes']:
                                inst_name = insts[note['inst']]
                                if (not self.playing) or self.isClosed:
                                    self.isPlaying = False
                                    break
                                if self.config['displayKeyboard']:
                                    self.keyboard.add({
                                        'note': note['pitch'] + offsets[inst_name] * 12,
                                        'channel': note['inst']
                                    })

                                message_utils.runmain(self.play_inst(
                                    note['pitch'], inst_name, 100, 0))
                                if note['time'] > 0:
                                    if self.config['displayKeyboard']:
                                        message_utils.runmain(self.updatekey())
                                        self.keyboard.reset()
                                    time.sleep(
                                        note['time'] * self.mcs['multiplier'] * 0.05)
                        elif self.mcs['version'] == 1:
                            for note in self.mcs['notes']:
                                inst_name = insts[note['inst']]
                                if (not self.playing) or self.isClosed:
                                    self.isPlaying = False
                                    break
                                if self.config['displayKeyboard']:
                                    self.keyboard.add({
                                        'note': note['pitch'] + offsets[inst_name] * 12,
                                        'channel': note['inst']
                                    })
                                if note['time'] > 0:
                                    if self.config['displayKeyboard']:
                                        message_utils.runmain(self.updatekey())
                                        self.keyboard.reset()
                                    time.sleep(
                                        note['time'] * self.mcs['multiplier'] * 0.05)

                                message_utils.runmain(self.play_inst(
                                    note['pitch'], inst_name, 100, 0))

                    else:
                        for msg in self.mid.play():
                            if (not self.playing) or self.isClosed:
                                self.isPlaying = False
                                break

                            if msg.type == "note_on" or msg.type == 'note_off':

                                if self.config['displayKeyboard']:
                                    try:
                                        if msg.type == 'note_off' or msg.velocity == 0:
                                            self.keyboard.remove({
                                                'note': msg.note,
                                                'channel': msg.channel
                                            })

                                        if msg.type == 'note_on' and msg.velocity != 0:
                                            self.keyboard.add({
                                                'note': msg.note,
                                                'channel': msg.channel
                                            })
                                        message_utils.runmain(self.updatekey())
                                    except:
                                        message_utils.warning(
                                            'unable to remove key')
                                if msg.type == 'note_on' and msg.velocity != 0:
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
                                if msg.control == 10:  # Pan
                                    if msg.value == 64:
                                        pan[msg.channel] = 0
                                    else:
                                        pan[msg.channel] = msg.value / 127 - 0.5
                                elif msg.control == 7:  # Channel Volume
                                    channel_volume[msg.channel] = msg.value / 127

                    if self.isPlaying:
                        if self.config['loop'] == 'song':
                            continue
                        else:
                            while True:
                                self.index += 1
                                if self.index > (len(self.file_list) - 1):
                                    self.index = 0
                                try:
                                    message_utils.runmain(
                                        self.open(self.index, False))
                                    break
                                except:
                                    message_utils.warning(
                                        'unable to open file ' + self.file_list[self.index])
                                    continue
                except Exception as e:
                    print(e)
                    if self.config['loop'] != 'song':
                        self.index += 1
                        try:
                            message_utils.runmain(
                                self.open(self.index, False))
                            break
                        except:
                            message_utils.warning(
                                'unable to open file ' + self.file_list[self.index])
                            continue
                    else:
                        self.isPlaying = False
            else:
                time.sleep(0.05)

    def set_midi(self, mid):
        self.mid = mido.MidiFile(mid)

    async def open(self, index, stop=True):
        if self.playing and stop:
            await self.stop()
        filename = self.file_list[index]
        await self.ws.send(
            message_utils.info(
                ref_strings.midiplayer.load_song.format(self.index, filename, message_utils.fileSize(filename))))
        if filename.endswith('.mcs') or filename.endswith('.mcz'):
            self.mcsMode = True
            self.mcs = mcsparser.read(filename)
        else:
            self.mcsMode = False
            self.set_midi(filename)
        if stop:
            self.play()

    def play(self):
        self.playing = True

    async def stop(self, args=None):
        self.keyboard.reset()
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
