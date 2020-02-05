import json
import math

from colorama import Back, Fore, Style

import ref_strings

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


def cmd(line, uuid="ffff0000-0000-0000-0000-000000000000"):
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
    print(Fore.WHITE+msg)

def info(msg):
    print(Fore.MAGENTA+msg)
    return cmd("say \u00a7d" + str(msg))


def warning(msg):
    print(Fore.YELLOW+msg)
    return cmd("say \u00a7d" + str(msg))


def error(msg):
    print(Fore.RED+msg)
    return cmd("say \u00a7c" + str(msg))


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


def setBlock(x, y, z, id, data=0):
    return cmd("setblock {0} {1} {2} {3} {4}".format(x, y, z, id, data))


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
    if entries != None:
        start = entries['start']
        for i in range(10):
            await ws.send(
                info('[§c{0}§d] - {1}'.format(i + start, entries['entries'][i])))
        await ws.send(
            info('第 {0} 页，共 {1} 页'.format(entries['page'], entries['maxpage'])))
    else:
        await ws.send(info(ref_strings.page_error))
