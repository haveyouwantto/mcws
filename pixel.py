from time import sleep
import math

from PIL import Image

import worldedit
import message_utils
import ref_strings
from mcws_module import Command, FileIOModule

# 以下为从 code connection 里复制的代码，原为js
# 进行了一些修改

# 方块颜色值
colors = [
    ['concrete', 0, 0xcfd5d6],
    ['concrete', 1, 0xe06100],
    ['concrete', 2, 0xa9309f],
    ['concrete', 3, 0x2389c6],
    ['concrete', 4, 0xf0af15],
    ['concrete', 5, 0x5ea818],
    ['concrete', 6, 0xd5658e],
    ['concrete', 7, 0x36393d],
    ['concrete', 8, 0x7d7d73],
    ['concrete', 9, 0x157788],
    ['concrete', 10, 0x641f9c],
    ['concrete', 11, 0x2c2e8f],
    ['concrete', 12, 0x603b1f],
    ['concrete', 13, 0x495b24],
    ['concrete', 14, 0x8e2020],
    ['concrete', 15, 0x080a0f],

    ['hardened_clay', 0, 0x985e43],
    ['stained_hardened_clay', 0, 0xd1b2a1],
    ['stained_hardened_clay', 1, 0xa15325],
    ['stained_hardened_clay', 2, 0x95586c],
    ['stained_hardened_clay', 3, 0x716c89],
    ['stained_hardened_clay', 4, 0xba8523],
    ['stained_hardened_clay', 5, 0x677534],
    ['stained_hardened_clay', 6, 0xa14e4e],
    ['stained_hardened_clay', 7, 0x392a23],
    ['stained_hardened_clay', 8, 0x876a61],
    ['stained_hardened_clay', 9, 0x565b5b],
    ['stained_hardened_clay', 10, 0x764656],
    ['stained_hardened_clay', 11, 0x4a3b5b],
    ['stained_hardened_clay', 12, 0x4d3323],
    ['stained_hardened_clay', 13, 0x4c532a],
    ['stained_hardened_clay', 14, 0x8f3d2e],
    ['stained_hardened_clay', 15, 0x251610]
]


def ColourDistance(rgb_1, rgb_2):
    R_1, G_1, B_1 = rgb_1
    R_2, G_2, B_2 = rgb_2
    rmean = (R_1 + R_2) / 2
    R = R_1 - R_2
    G = G_1 - G_2
    B = B_1 - B_2
    return math.sqrt((2 + rmean / 256) * (R ** 2) + 4 * (G ** 2) + (2 + (255 - rmean) / 256) * (B ** 2))


def colorToBlock(color):
    try:
        # find exact match...
        i = colors.index(color)
        return i
    except ValueError:
        # approximate
        i = -1
        rgb = ((color >> 16) & 0xff), ((color >> 8) & 0xff), (color & 0xff)

        # 存储最小的色差
        best = 0xffffffff

        # 将该颜色与所有方块颜色比较
        for j in range(len(colors)):
            c = colors[j]

            # 获取该颜色与方块颜色的色差
            dc = ColourDistance(rgb, (((c[2] >> 16) & 0xff), ((c[2] >> 8) & 0xff), (c[2] & 0xff)))

            # 如果色差比之前的更小
            if (i < 0 or dc < best):
                i = j
                best = dc

        return colors[i]


# 以上

class PixelGenerator(FileIOModule):
    def __init__(self, ws, we):
        FileIOModule.__init__(self, ws, "images/", (".png", ".jpg", ".bmp"))
        self.we = we
        self.commands['--list']['command'].description = ref_strings.pixel.help['--list']
        self.commands['--search']['command'].description = ref_strings.pixel.help['--search']
        self.commands['--reload']['command'].description = ref_strings.pixel.help['--reload']
        self.add_command(Command('--draw', ('-d',), ref_strings.pixel.help['--draw']), self.open_file)

    async def open(self, filename):
        await self.generate(filename, await self.we.getPlayerBlockPos())

    async def generate(self, filename, position):
        img = Image.open(filename)
        size = img.size

        await self.ws.send(message_utils.cmd('closechat'))
        await self.ws.send(message_utils.info(
            ref_strings.pixel.image_info.format(filename, size[0], size[1],
                                                message_utils.filesize(filename))))

        max_width = 256

        if size[0] > max_width:
            ratio = size[0] / size[1]
            resize = max_width, int(max_width / ratio)
            img = img.resize(resize)
            size = resize
            await self.ws.send(message_utils.info(ref_strings.pixel.resize_info.format(size[0], size[1])))

        for y in range(size[1]):
            for x in range(size[0]):
                px = img.getpixel((x, y))

                # RGBA 图片
                if len(px) == 4:
                    # 检测透明度，如果小于128则不放置方块
                    if px[3] < 0x80:
                        continue

                # 获取整数颜色值
                color = (px[0] << 16) | (px[1] << 8) | px[2]

                blockToPlace = colorToBlock(color)

                await worldedit.setblock(self.ws, worldedit.Position(position.x + x, position.y, position.z + y),
                                         blockToPlace[0],
                                         blockToPlace[1])
                # 限制指令执行速度
                sleep(0.002)
