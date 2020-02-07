import ref_strings
import message_utils
import fileutils


class Command:
    def __init__(self, cmd, alias):
        self.cmd = cmd
        self.alias = alias


class BaseModule:
    def __init__(self, ws):
        self.commands = []
        self.ws = ws
        self.add_command(Command('--help', ('-h', '-?')), self.help)
        self.add_command(Command('--info', ('-i',)), self.info)

    async def help(self, args):
        pass

    async def info(self, args):
        pass

    def add_command(self, cmd, onCommand):
        self.commands.append((cmd, onCommand))

    async def no_command(self):
        pass

    async def parse_command(self, args):
        if len(args) == 0:
            await self.no_command()
            return
        for i in self.commands:
            if i[0].cmd == args[0]:
                await i[1](args[1:])
                return
            for j in i[0].alias:
                if j == args[0]:
                    await i[1](args[1:])
                    return
        await self.ws.send(message_utils.error(ref_strings.unknown_command))


class FileIOModule(BaseModule):
    def __init__(self, ws, path, extensions):
        BaseModule.__init__(self, ws)
        self.path = path
        self.extensions = extensions
        self.add_command(Command('--search', ('-s',)), self.search_file)
        self.add_command(Command('--list', ('-ls',)), self.list_file)
        self.add_command(Command('--reload', ('-re',)), self.reload)
        self.get_file_list()

    def get_file_list(self):
        self.file_list = fileutils.listFile(self.path, self.extensions)

    async def list_file(self, args):
        page = 1
        if len(args) != 0:
            page = int(args[1])
        entries = message_utils.getPage(self.file_list, page)
        await message_utils.printEntries(self.ws, entries)

    async def search_file(self, args):
        results = self.search(args)
        if len(results) == 0:
            await self.ws.send(message_utils.error(ref_strings.empty_result))
        else:
            for i in results:
                await self.ws.send(
                    message_utils.info(ref_strings.list_format.format(i[0], i[1])))

    async def open_file(self, args):
        if len(args) == 0:
            return
        try:
            arg1 = int(args[0])
            if arg1 < len(self.file_list):
                await self.open(self.file_list[arg1])
            else:
                await self.ws.send(message_utils.error(ref_strings.file_not_exists))
        except ValueError:
            await self.ws.send(message_utils.error(ref_strings.invaild_id))

    async def open(self, filename):
        pass

    async def reload(self, args):
        self.get_file_list()
        await self.ws.send(message_utils.info(ref_strings.module.reload))

    def search(self, args):
        keyword = ' '.join(args)
        self.lastQuery = keyword
        results = []
        keyword = keyword.lower().split(' ')
        for i in range(len(self.file_list)):
            element = self.file_list[i].lower()
            priority = 0
            for j in keyword:
                if j in element:
                    priority += 1
            if priority == len(keyword):
                results.append((i, self.file_list[i]))
        return results
