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

helpmsg={
    '.test':'测试用命令    \u00a7a.test',
    '.help':'提供帮助/命令列表    \u00a7a.help',
    '.function':'运行在相应的功能文件中找到的命令    \u00a7a.function <function>',
    '.midi':'播放一个mid文件    \u00a7a.midi <file>'
}


def getChat(msg):
    return msg["body"]["properties"]["Message"]


def info(msg):
    return cmd("say \u00a7d"+str(msg))


def play_note(midimsg):

    origin = midimsg.note-66
    pitch= 2**(origin/12)
    volume=midimsg.velocity/128
    if midimsg.channel==10:
        return cmd("")
    return cmd("playsound note.harp @a ^0 ^ ^ "+str(volume)+" "+str(pitch))


async def hello(websocket, path):
    await websocket.send(sub)
    sender = "外部"
    while True:
        data = await websocket.recv()
        msg = json.loads(data)
        print(data)
        if msg["header"]["messagePurpose"] == "event":

            if msg["body"]["eventName"] == "PlayerMessage" and msg["body"]["properties"]["Sender"] != sender:

                args = getChat(msg).split(" ")

                if(args[0] == ".test"):
                    await websocket.send(info("Hello World"))

                if args[0]==".help":
                    for i in helpmsg:
                        await websocket.send(info(i+" - "+helpmsg[i]))

                if args[0] == ".function":
                    if len(args)>1:
                        if args[1]=="-ls":
                            for filename in glob.glob("functions/*.mcfunction"):
                                await websocket.send(info(filename))
                        else:
                            if os.path.exists("functions/"+args[1]+".mcfunction"):
                                with open("functions/"+args[1]+".mcfunction", "r") as file:
                                    for i in file.readlines():
                                        await websocket.send(cmd(i))
                            else:
                                await websocket.send(info("文件不存在"))
                    else:
                        pass

                if args[0] == ".midi":
                    if len(args)>1:
                        if args[1]=="-ls":
                            for filename in glob.glob("midis/*.mid"):
                                await websocket.send(info(filename))
                        else:
                            if os.path.exists("midis/"+args[1]+".mid"):
                                await websocket.send(info("正在加载 "+args[1]+".mid ..."))
                                mid = mido.MidiFile("midis/"+args[1]+".mid")
                                for msg in mid.play():
                                    if msg.type == "note_on":
                                        print(msg)
                                        await websocket.send(play_note(msg))
                            else:
                                await websocket.send(info("文件不存在"))
                    else:
                        pass

        elif msg["header"]["messagePurpose"] == "commandResponse":
            pass

start_server = websockets.serve(hello, "localhost", 19210)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
