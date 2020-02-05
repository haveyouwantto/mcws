import message_utils
import json


class Position:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __mul__(self, other):
        return (1 + abs(self.x - other.x)) * (1 + abs(self.y - other.y)) * (1 + abs(self.z - other.z))

    def __str__(self):
        return "{0} {1} {2}".format(self.x, self.y, self.z)

    def getSpeed(self, other):
        return (
            abs(self.x-other.x)**2 +
            abs(self.y-other.y)**2 +
            abs(self.z-other.z)**2
        )**1/2


async def fill(ws, pos1, pos2, blockname, blockdata=0):
    await ws.send(message_utils.cmd("fill {0} {1} {2} {3}".format(pos1, pos2, blockname, blockdata)))
    msg = json.loads(await ws.recv())
    if msg["body"]["statusCode"] == -2147483648:
        return {
            "success": False,
            "data": msg["body"]["statusMessage"]
        }
    else:
        return {
            "success": True,
            "data": "已填充{0}个{1}".format(msg["body"]["fillCount"], msg["body"]["blockName"])
        }


def sort(a, b):
    l = [a, b]
    return sorted(l)


async def getPlayerPos(ws):
    await ws.send(message_utils.cmd('querytarget @s'))
    data = await ws.recv()
    msg = json.loads(data)
    detail = json.loads(msg["body"]["details"])[0]
    x = detail["position"]["x"]
    y = detail["position"]["y"]
    z = detail["position"]["z"]
    return Position(x, y, z)


async def getPlayerBlockPos(ws):
    await ws.send(message_utils.cmd('testforblock ~ ~ ~ air'))
    data = await ws.recv()
    msg = json.loads(data)
    print(msg)
    x = msg["body"]["position"]["x"]
    y = msg["body"]["position"]["y"]
    z = msg["body"]["position"]["z"]
    return Position(x, y, z)


def intPos(pos):
    return Position(int(pos.x), int(pos.y), int(pos.z))


def parseCmd(ws, args):
    if args[0] == ".set":
        if(len(args) == 1 or args[1] == ''):
            await ws.send(message_utils.error('语法错误'))
            return
        if args[1] == "1":
            pos1 = await worldedit.getPlayerBlockPos(ws)
            if pos2 == None:
                pos2 = pos1
            await ws.send(
                message_utils.info(
                    '坐标1: {0} ({1})'.format(
                        str(pos1), pos1 * pos2
                    )
                )
            )
        if args[1] == "2":
            pos2 = await worldedit.getPlayerBlockPos(ws)
            if pos1 == None:
                pos1 = pos2
            await ws.send(
                message_utils.info(
                    '坐标2: {0} ({1})'.format(
                        str(pos2), pos1 * pos2
                    )
                )
            )

    if args[0] == ".fill":
        if(len(args) == 1 or args[1] == ''):
            await ws.send(message_utils.error('语法错误'))
            return
        if pos1 == None or pos2 == None:
            await ws.send(message_utils.error('未设置坐标'))
            return
        result=await worldedit.fill(ws,pos1,pos2,args[1])
        if result["success"]:
            await ws.send(message_utils.info(result["data"]))
        else:
            await ws.send(message_utils.error(result["data"]))
