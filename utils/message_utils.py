import json
import math
import os

from static import stats, ref_strings
from utils import uuidgen
from user_interface import coloreplace

log_command = False

sub = json.dumps({
    "body": {
        "eventName": "PlayerMessage"
    },
    "header": {
        "requestId": "00000000-0000-0000-0000-000000000000",
        "messagePurpose": "subscribe",
        "version": 1,
        "messageType": "commandRequest"
    }
})


def autocmd(line):
    return cmd(line, uuidgen.gen())


def cmd(line, uuid):
    if log_command:
        print(coloreplace.replace(line))
    stats.commands += 1
    return json.dumps({
        "body": {
            "origin": {
                "type": "player"
            },
            "commandLine": line,
            "version": 1
        },
        "header": {
            "requestId": uuid,
            "messagePurpose": "commandRequest",
            "version": 1,
            "messageType": "commandRequest"
        }
    })


def getChat(msg):
    return msg["body"]["properties"]["Message"]


def log(msg):
    print(coloreplace.replace(str(msg)))


def info(msg):
    print(coloreplace.replace("\u00a7d" + str(msg)))
    return autocmd("say \u00a7d" + str(msg))


def warning(msg):
    print(coloreplace.replace("\u00a7e" + str(msg)))
    return autocmd("say \u00a7e" + str(msg))


def error(msg):
    print(coloreplace.replace("\u00a7c" + str(msg)))
    return autocmd("say \u00a7c" + str(msg))


def drawKeyboard(key, start=0):
    out = ""
    i = start
    while i < key:
        if i % 12 == 1 or i % 12 == 3 or i % 12 == 6 or i % 12 == 8 or i % 12 == 10:
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

    return autocmd(out + '"}]}')


def setBlock(x, y, z, _id, data=0):
    return autocmd("setblock {0} {1} {2} {3} {4}".format(x, y, z, _id, data))


def getPage(_list, page):
    maxpage = math.ceil(len(_list) / 10)
    if page > maxpage:
        return None
    start = (page - 1) * 10
    out = _list[start:start + 10]
    return {
        'start': start,
        'entries': out,
        'page': page,
        'maxpage': maxpage
    }


async def printEntries(ws, entries):
    if entries is not None:
        try:
            start = entries['start']
            string = '\n'
            for i in range(10):
                string += ref_strings.list_format.format(
                    i + start, entries['entries'][i])+'\n'
            string += ref_strings.pagenum_format.format(
                entries['page'], entries['maxpage'])
            await ws.send(info(string))
        except IndexError:
            return
    else:
        await ws.send(error(ref_strings.page_error))


def runmain(coroutine):
    try:
        coroutine.send(None)
    except StopIteration as e:
        return e.value


suffix = ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']


def toSI(n, binaryMode=False):
    if n < 1000:
        return "{0:.3g} ".format(n)
    if binaryMode:
        k = 1024
    else:
        k = 1000
    for i in suffix:
        if n < k:
            if binaryMode:
                return "{0:.3g} {1}i".format(n, i)
            else:
                return "{0:.3g} {1}".format(n, i)

        n /= k


def fileSize(filename):
    size = os.path.getsize(filename)
    return toSI(size, True) + 'B'


def formatNumber(n):
    if n == 0:
        return ''
    else:
        return '{:.4n}'.format(n)
