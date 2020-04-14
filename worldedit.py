import json
import time

import message_utils
import ref_strings

import uuidgen


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
                       abs(self.x - other.x) ** 2 +
                       abs(self.y - other.y) ** 2 +
                       abs(self.z - other.z) ** 2
               ) ** 1 / 2


def smaller(a, b):
    if a < b:
        return [a, b]
    else:
        return [b, a]


def intPos(pos):
    return Position(int(pos.x), int(pos.y), int(pos.z))


def getSize(pos1, pos2):
    return (
        abs(pos1.x - pos2.x),
        abs(pos1.y - pos2.y),
        abs(pos1.z - pos2.z)
    )


def generateCoorSequence(pos1, pos2):
    dimension = getSize(pos1, pos2)
    if pos1 * pos2 <= 32768:
        return {
            "size": pos1 * pos2, "dimension": dimension, "sequence": [(pos1, pos2)]
        }
    else:
        out = {
            "size": pos1 * pos2, "dimension": dimension, "sequence": []
        }
        xs = smaller(pos1.x, pos2.x)
        ys = smaller(pos1.y, pos2.y)
        zs = smaller(pos1.z, pos2.z)
        for x in range(xs[0], xs[1] + 1, 32):
            for y in range(ys[0], ys[1] + 1, 32):
                for z in range(zs[0], zs[1] + 1, 32):
                    if xs[1] - x < 32:
                        x2 = xs[1]
                    else:
                        x2 = x + 31
                    if ys[1] - y < 32:
                        y2 = ys[1]
                    else:
                        y2 = y + 31
                    if zs[1] - z < 32:
                        z2 = zs[1]
                    else:
                        z2 = z + 31
                    out['sequence'].append(
                        (Position(x, y, z), Position(x2, y2, z2))
                    )
        return out

# print(generateCoorSequence(Position(127,62,143),Position(-128,62,-112)))


class WorldEdit:

    def __init__(self, ws):
        self.ws = ws
        self.pos1 = None
        self.pos2 = None

    async def parseCmd(self, args):
        if args[0] == ".set":
            if (len(args) == 1 or args[1] == ''):
                await self.ws.send(message_utils.error(ref_strings.command_error))
                return
            if args[1] == "1":
                self.pos1 = await self.getPlayerBlockPos()
                if self.pos2 == None:
                    self.pos2 = self.pos1
                await self.ws.send(
                    message_utils.info(
                        ref_strings.worldedit.coor_1_msg.format(
                            str(self.pos1), self.pos1 * self.pos2
                        )
                    )
                )
            if args[1] == "2":
                self.pos2 = await self.getPlayerBlockPos()
                if self.pos1 == None:
                    self.pos1 = self.pos2
                await self.ws.send(
                    message_utils.info(
                        ref_strings.worldedit.coor_2_msg.format(
                            str(self.pos2), self.pos1 * self.pos2
                        )
                    )
                )
            await self.ws.send(message_utils.autocmd('closechat'))

        if args[0] == ".fill":
            if (len(args) == 1 or args[1] == ''):
                await self.ws.send(message_utils.error(ref_strings.command_error))
                return
            if self.pos1 == None or self.pos2 == None:
                await self.ws.send(message_utils.error(ref_strings.worldedit.no_coordinate))
                return
            if len(args) == 2:
                result = await self.fillAny(args[1])
            else:
                result = await self.fillAny(args[1], args[2])
            if result["success"]:
                await self.ws.send(message_utils.info(result["data"]))
            else:
                await self.ws.send(message_utils.error(result["data"]))

    async def fillAny(self, blockname, blockdata=0):
        sequence = generateCoorSequence(self.pos1, self.pos2)
        await self.ws.send(message_utils.autocmd('closechat'))
        for i in sequence['sequence']:
            await self.ws.send(message_utils.autocmd("fill {0} {1} {2} {3}".format(i[0], i[1], blockname, blockdata)))
            time.sleep(0.01)
        return {
            "success": True,
            "data": ref_strings.worldedit.fill_message.format(sequence['size'])
        }

    async def getPlayerPos(self):
        await self.ws.send(message_utils.autocmd('querytarget @s'))
        data = await self.ws.recv()
        msg = json.loads(data)
        while msg.get('body').get('details') == None:
            await self.ws.send(message_utils.autocmd('querytarget @s'))
            data = await self.ws.recv()
            msg = json.loads(data)
        detail = json.loads(msg.get('body').get('details'))[0]
        x = detail["position"]["x"]
        y = detail["position"]["y"]
        z = detail["position"]["z"]
        return Position(x, y, z)

    async def getPlayerBlockPos(self):
        await self.ws.send(message_utils.autocmd('testforblock ~ ~ ~ air'))
        data = await self.ws.recv()
        msg = json.loads(data)
        while msg.get('body').get('position') == None:
            await self.ws.send(message_utils.autocmd('testforblock ~ ~ ~ air'))
            data = await self.ws.recv()
            msg = json.loads(data)
        x = msg["body"]["position"]["x"]
        y = msg["body"]["position"]["y"]
        z = msg["body"]["position"]["z"]
        return Position(x, y, z)

    async def isBlock(self,pos, block):
        uuid = uuidgen.gen()
        await self.ws.send(message_utils.cmd('testforblock {0} {1}'.format(pos, block),uuid))
        data = await self.ws.recv()
        msg = json.loads(data)
        while msg.get('header').get('requestId') != uuid:
            continue
        return msg["body"]["matches"]

    async def setblock(self,pos, blockname, blockdata=0):
        cmd = 'setblock {0} {1} {2}'.format(pos, blockname, blockdata)
        await self.ws.send(message_utils.autocmd(cmd))

    async def fill(self,pos1, pos2, blockname, blockdata=0):
        cmd = 'fill {0} {1} {2} {3}'.format(pos1, pos2, blockname, blockdata)
        await self.ws.send(message_utils.autocmd(cmd))

    async def copyBlock(self,source,destination):
        cmd = 'clone {0} {0} {1}'.format(source, destination)
        await self.ws.send(message_utils.autocmd(cmd))