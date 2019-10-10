import asyncio
import websockets
import json
import time
import mido
import os
import glob


def cmd(line):
    return json.dumps({
        "body": {
            "origin": {
                "type": "player"
            },
            "commandLine": line,
            "version": 1
        },
        "header": {
            "requestId": "ffff0000-0000-0000-0000-000000000000",
            "messagePurpose": "commandRequest",
            "version": 1,
            "messageType": "commandRequest"
        }
    })


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

helpmsg = {
    '.test': '测试用命令    \u00a7a.test',
    '.help': '提供帮助/命令列表    \u00a7a.help',
    '.function': '运行在相应的功能文件中找到的命令    \u00a7a.function <function>',
    '.midi': '播放一个mid文件    \u00a7a.midi <file>'
}


def getChat(msg):
    return msg["body"]["properties"]["Message"]


def info(msg):
    return cmd("say \u00a7d"+str(msg))


def play_note(midimsg):

    origin = midimsg.note-66
    pitch = 2**(origin/12)
    volume = midimsg.velocity/128
    if midimsg.channel == 10:
        return cmd("")
    return cmd("playsound note.harp @a ^0 ^ ^ "+str(volume)+" "+str(pitch))



def setBlock(x, y, z, id, data=0):
    return cmd("setblock "+str(x)+" "+str(y)+" "+str(z)+" "+str(id)+" "+str(data))


async def hello(ws, path):
    await ws.send(sub)
    sender = "外部"
    while True:
        data = await ws.recv()
        msg = json.loads(data)
        print(data)
        if msg["header"]["messagePurpose"] == "event":

            if msg["body"]["eventName"] == "PlayerMessage" and msg["body"]["properties"]["Sender"] != sender:

                raw=getChat(msg)
                args = raw.split(" ")

                if(args[0] == ".test"):
                    await ws.send(info("Hello World"))

                if args[0] == ".help":
                    for i in helpmsg:
                        await ws.send(info(i+" - "+helpmsg[i]))

                if raw.startswith(".function"):
                    arg1 = raw[10:]
                    if arg1 == "-ls":
                        for filename in glob.glob("functions/*.mcfunction"):
                            await ws.send(info(filename))
                    else:
                        if os.path.exists("functions/"+arg1+".mcfunction"):
                            with open("functions/"+arg1+".mcfunction", "r") as file:
                                for i in file.readlines():
                                    await ws.send(cmd(i))
                        else:
                            await ws.send(info("文件不存在"))

                if raw.startswith(".midi"):
                    arg1 = raw[6:]
                    print(arg1)
                    if arg1 == "-ls":
                        for filename in glob.glob("midis/*.mid"):
                            await ws.send(info(filename))
                    else:
                        if os.path.exists("midis/"+arg1+".mid"):
                            await ws.send(info("正在加载 "+arg1+".mid ..."))
                            try:
                                mid = mido.MidiFile("midis/"+arg1+".mid")
                                for msg in mid.play():
                                    if msg.type == "note_on":
                                        print(msg)
                                        await ws.send(play_note(msg))
                            except:
                                await ws.send(info("无法打开文件！"))
                        else:
                            await ws.send(info("文件不存在"))

                if args[0] == ".sier":
                    px=50200
                    py=100
                    pz=50000
                    for x in range(-50,50):
                        for z in range(-50,50):
                            y=x^z
                            await ws.send(setBlock(px+x,py+y,pz+z,"redstone_block"))
                            time.sleep(0.001)

        elif msg["header"]["messagePurpose"] == "commandResponse":
            pass

start_server = websockets.serve(hello, "localhost", 19111)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
