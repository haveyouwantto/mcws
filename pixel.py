from time import sleep
import math

from PIL import Image

import worldedit
import message_utils
import ref_strings
from mcws_module import Command, FileIOModule
import downloader

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

pal = [207, 213, 214, 224, 97, 0, 169, 48, 159, 35, 137, 198, 240, 175, 21, 94, 168, 24, 213, 101, 142, 54, 57, 61, 125,
       125, 115, 21, 119, 136, 100, 31, 156, 44, 46, 143, 96, 59, 31, 73, 91, 36, 142, 32, 32, 8, 10, 15,
       152, 94, 67, 209, 178, 161, 161, 83, 37, 149, 88, 108, 113, 108, 137, 186, 133, 35, 103, 117, 52, 161, 78, 78,
       57, 42, 35, 135, 106, 97, 86, 91, 91, 118, 70, 86, 74, 59, 91, 77, 51, 35, 76, 83, 42, 143, 61, 46, 37, 22, 16]


def RGBToHSV(rgb):
    r1 = rgb[0] / 255
    g1 = rgb[1] / 255
    b1 = rgb[2] / 255
    cmax = max(r1, g1, b1)
    cmin = min(r1, g1, b1)
    delta = cmax - cmin

    if delta == 0:
        h = 0
    elif cmax == r1:
        h = 60 * ((g1 - b1) / delta + 0)
    elif cmax == g1:
        h = 60 * ((g1 - b1) / delta + 0)
    elif cmax == b1:
        h = 60 * ((g1 - b1) / delta + 0)

    if cmax == 0:
        s = 0
    else:
        s = delta / cmax

    v = cmax

    return (h, s, v)


def ColourDistance(rgb_1, rgb_2):
    R_1, G_1, B_1 = rgb_1
    R_2, G_2, B_2 = rgb_2
    rmean = (R_1 + R_2) / 2
    R = R_1 - R_2
    G = G_1 - G_2
    B = B_1 - B_2
    return math.sqrt((2 + rmean / 256) * (R ** 2) + 4 * (G ** 2) + (2 + (255 - rmean) / 256) * (B ** 2))


# deprecated
def colordistance(rgb_1, rgb_2):
    return abs(rgb_1[0] - rgb_2[0]) + abs(rgb_1[1] - rgb_2[1]) + abs(rgb_1[2] - rgb_2[2])


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

            dc = ColourDistance(
                rgb, (((c[2] >> 16) & 0xff), ((c[2] >> 8) & 0xff), (c[2] & 0xff)))

            # 如果色差比之前的更小
            if (i < 0 or dc < best):
                i = j
                best = dc

        return colors[i]


# 以上

class PixelGenerator(FileIOModule):
    def __init__(self, ws, we):
        FileIOModule.__init__(self, ws, "images/",
                              (".png", ".jpg", ".bmp"), 'PixelGenerator')
        self.we = we
        self.mode = '+x+z'
        self.modes = ['+x+z', '+x-z', '-x+z',
                      '-x-z', '+x-y', '-x-y', '+z-y', '-z-y']
        self.commands['--list']['command'].description = ref_strings.pixel.help['--list']
        self.commands['--search']['command'].description = ref_strings.pixel.help['--search']
        self.commands['--reload']['command'].description = ref_strings.pixel.help['--reload']
        self.add_command(
            Command('--draw', ('-d',), ref_strings.pixel.help['--draw']), self.open_file)
        self.add_command(
            Command('--mode', ('-m',), ref_strings.pixel.help['--mode']), self.set_mode)
        self.add_command(Command('--man-mode', ('-mm',),
                                 ref_strings.pixel.help['--man-mode']), self.man_mode)
        self.add_command(Command('--from-url', ('-u',),
                                 ref_strings.pixel.help['--from-url']), self.from_url)
        self.add_command(Command('--dither', ('-di',), 'dither'), self.set_dither)
        self.add_command(Command('--big', ('-b',), 'big'), self.set_big)

        self.default_config = {
            'big': False,
            'dither': False
        }

    async def set_big(self, args):
        if len(args) > 0:
            if args[0] == '0':
                self.config['big'] = False
            elif args[0] == '1':
                self.config['big'] = True
        else:
            await self.ws.send(message_utils.info(ref_strings.pixel.current_mode.format(self.mode)))

    async def set_dither(self, args):
        if len(args) > 0:
            if args[0] == '0':
                self.config['dither'] = False
            elif args[0] == '1':
                self.config['dither'] = True
        else:
            await self.ws.send(message_utils.info(ref_strings.pixel.current_mode.format(self.mode)))

    async def from_url(self, args):
        pos = await self.we.getPlayerBlockPos()
        await self.ws.send(message_utils.info(ref_strings.pixel.download_image.format(args[0])))
        if len(args) == 0:
            return
        code = downloader.download_image(args[0])
        if code[0] == -1:
            await self.ws.send(message_utils.error(ref_strings.pixel.web_error.format(args[0])))
            return
        if code[0] == 1:
            await self.ws.send(message_utils.error(ref_strings.pixel.mime_error.format(code[1])))
            return
        await self.generate('cache/img', pos)

    async def man_mode(self, args):
        for i in ref_strings.pixel.mode_help:
            await self.ws.send(message_utils.info(i))
        for i in self.modes:
            await self.ws.send(message_utils.info(i))

    def get_position(self, position, imagesize, imagepos, setblock):
        if self.mode == '+x+z':
            pos1 = worldedit.Position(
                position.x + imagepos[0], position.y, position.z + imagepos[1])
        elif self.mode == '+x-z':
            pos1 = worldedit.Position(
                position.x + imagepos[0], position.y, position.z - imagepos[1])
        elif self.mode == '-x+z':
            pos1 = worldedit.Position(
                position.x - imagepos[0], position.y, position.z + imagepos[1])
        elif self.mode == '-x-z':
            pos1 = worldedit.Position(
                position.x - imagepos[0], position.y, position.z - imagepos[1])
        elif self.mode == '+x-y':
            pos1 = worldedit.Position(position.x + imagepos[0], position.y + imagesize[1] - imagepos[1] - 1,
                                      position.z)
        elif self.mode == '-x-y':
            pos1 = worldedit.Position(position.x - imagepos[0], position.y + imagesize[1] - imagepos[1] - 1,
                                      position.z)
        elif self.mode == '+z-y':
            pos1 = worldedit.Position(position.x, position.y + imagesize[1] - imagepos[1] - 1,
                                      position.z + imagepos[0])
        else:  # -z-y
            pos1 = worldedit.Position(position.x, position.y + imagesize[1] - imagepos[1] - 1,
                                      position.z - imagepos[0])
        if not setblock:
            if self.mode == '+x+z':
                pos2 = worldedit.Position(
                    position.x + imagepos[0] + imagepos[2], position.y, position.z + imagepos[1])
            elif self.mode == '+x-z':
                pos2 = worldedit.Position(
                    position.x + imagepos[0] + imagepos[2], position.y, position.z - imagepos[1])
            elif self.mode == '-x+z':
                pos2 = worldedit.Position(
                    position.x - imagepos[0] - imagepos[2], position.y, position.z + imagepos[1])
            elif self.mode == '-x-z':
                pos2 = worldedit.Position(
                    position.x - imagepos[0] - imagepos[2], position.y, position.z - imagepos[1])
            elif self.mode == '+x-y':
                pos2 = worldedit.Position(position.x + imagepos[0] + imagepos[2],
                                          position.y + imagesize[1] - imagepos[1] - 1, position.z)
            elif self.mode == '-x-y':
                pos2 = worldedit.Position(position.x - imagepos[0] - imagepos[2],
                                          position.y + imagesize[1] - imagepos[1] - 1, position.z)
            elif self.mode == '+z-y':
                pos2 = worldedit.Position(position.x, position.y + imagesize[1] - imagepos[1] - 1,
                                          position.z + imagepos[0] + imagepos[2])
            else:  # -z-y
                pos2 = worldedit.Position(position.x, position.y + imagesize[1] - imagepos[1] - 1,
                                          position.z - imagepos[0] - imagepos[2])
            return (pos1, pos2)
        else:
            return pos1

    async def set_mode(self, args):
        if len(args) > 0:
            if args[0] in self.modes:
                self.mode = args[0]
                await self.ws.send(message_utils.info(ref_strings.pixel.set_mode.format(self.mode)))
            else:
                await self.ws.send(message_utils.error(ref_strings.pixel.invaild_mode))
        else:
            await self.ws.send(message_utils.info(ref_strings.pixel.current_mode.format(self.mode)))

    async def open(self, index):
        pos = await self.we.getPlayerBlockPos()
        await self.generate(self.file_list[index], pos)

    async def generate(self, filename, position):
        img = Image.open(filename)
        size = img.size

        await self.ws.send(message_utils.autocmd('closechat'))
        await self.ws.send(message_utils.info(
            ref_strings.pixel.image_info.format(filename, size[0], size[1],
                                                message_utils.filesize(filename))))
        max_width = 16 << 4

        if (not self.config['big']) and size[0] > max_width:
            ratio = size[0] / size[1]
            resize = max_width, int(max_width / ratio)
            img = img.resize(resize)
            size = resize
            await self.ws.send(message_utils.info(ref_strings.pixel.resize_info.format(size[0], size[1])))

        if self.config['dither']:
            try:
                palimage = Image.new('P', (16, 16))
                palimage.putpalette(pal * 7)
                img = img.convert('RGB').quantize(palette=palimage)
                img.save('cache/test.png', 'png')
            except Exception as e:
                print(e)
                return

        if self.config['big']:
            block_size = 128
            work = 0
            required = math.ceil(size[0] / block_size) * math.ceil(size[1] / block_size)
            await self.ws.send(message_utils.info('block size = {0}'.format(block_size)))
            for x in range(0, size[0], block_size):
                for y in range(0, size[1], block_size):
                    if size[0] - x < block_size:
                        x2 = size[0]
                    else:
                        x2 = x + block_size - 1
                    if size[1] - y < block_size:
                        y2 = size[1]
                    else:
                        y2 = y + block_size - 1
                    print(x, y, x2, y2)
                    tempimage = img.crop((x, y, x2 + 1, y2 + 1))
                    temppos = worldedit.Position(position.x + x, position.y,
                                                 position.z + y)
                    print(temppos)
                    await self.ws.send(message_utils.info('{0}/{1}'.format(work, required)))
                    sleep(1)
                    await self.ws.send(message_utils.autocmd('tp @p ' + str(temppos)))
                    await self.draw(tempimage, temppos)
                    work += 1
                    sleep(1)
            return

        await self.draw(img, position)

    async def draw(self, img, position):
        size = img.size
        pal = img.getpalette()
        pxs = {}

        for y in range(size[1]):
            lastpixel = None
            for x in range(size[0]):
                px = img.getpixel((x, y))

                # PAL8 图片
                if isinstance(px, int):
                    index = px * 3
                    color = (pal[index] << 16) | (
                            pal[index + 1] << 8) | pal[index + 2]

                # RGB 图片
                elif len(px) == 3:
                    color = (px[0] << 16) | (px[1] << 8) | px[2]

                # RGBA 图片
                elif len(px) == 4:
                    # 检测透明度，如果小于128则不放置方块
                    if px[3] < 0x80:
                        lastpixel = None
                        continue

                    # 获取整数颜色值
                    color = (px[0] << 16) | (px[1] << 8) | px[2]

                blockToPlace = colorToBlock(color)
                fmt = "{0} {1}".format(blockToPlace[0], blockToPlace[1])

                if fmt in pxs:
                    if lastpixel == fmt:
                        pxs[fmt][-1][2] += 1
                    else:
                        pxs[fmt].append([x, y, 0])
                else:
                    pxs[fmt] = [[x, y, 0]]

                lastpixel = fmt

        await self.ws.send(message_utils.info(ref_strings.pixel.start))

        for i in pxs:
            blockToPlace = i.split(" ")
            for j in pxs[i]:
                if j[2] == 0:
                    pos = self.get_position(position, size, j, True)
                    await self.we.setblock(pos,
                                           blockToPlace[0],
                                           int(blockToPlace[1]))
                else:
                    pos = self.get_position(position, size, j, False)
                    await self.we.fill(pos[0],
                                       pos[1],
                                       blockToPlace[0],
                                       int(blockToPlace[1]))

                sleep(0.002)

        await self.ws.send(message_utils.info(ref_strings.pixel.finish))
