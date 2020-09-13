from static import ref_strings
from utils import fileutils, message_utils

import os
import traceback
import sys
from json import dumps


class Command:
    def __init__(self, cmd, alias, description=""):
        self.cmd = cmd
        self.alias = alias
        self.description = description

    def __str__(self):
        alias_str = ""
        for i in self.alias:
            alias_str = alias_str + i + " "
        return "{0}, {1}    {2}".format(self.cmd, alias_str, self.description)


class BaseModule:
    def __init__(self, ws, name='', description=''):
        self.commands = {}
        self.ws = ws
        self.module_id = self.__class__.__name__
        self.module_name = name
        self.description = description
        self.add_command(Command('--help', ('-h', '-?', 'help'),
                                 ref_strings.module.help['--help']), self.help)
        self.add_command(Command('--info', ('-i', 'info'),
                                 ref_strings.module.help['--info']), self.info)
        self.add_command(Command('--print-data', ('-pd',),
                                 ref_strings.module.help['--list-config']), self.print_data)
        self.config = {}
        self.default_config = {}

    async def help(self, args):
        string = '\n' + '{0} - {1}'.format(self.module_name, self.description)+'\n'
        for i in self.commands:
            string += str(self.commands[i]["command"])+'\n\u00a7d'
        await self.ws.send(message_utils.info(string))

    async def info(self, args):
        pass

    def add_command(self, cmd, onCommand):
        self.commands[cmd.cmd] = {
            "command": cmd,
            "onCommand": onCommand
        }

    async def no_command(self):
        pass

    async def parse_command(self, args):
        try:
            if len(args) == 0:
                await self.no_command()
                return
            for i in self.commands:
                if i == args[0]:
                    await self.commands[i]["onCommand"](args[1:])
                    return
                for j in self.commands[i]["command"].alias:
                    if j == args[0]:
                        await self.commands[i]["onCommand"](args[1:])
                        return
            await self.ws.send(message_utils.error(ref_strings.unknown_command))
        except Exception as e:
            await self.ws.send(message_utils.error('{0}: {1}'.format(type(e).__name__, e)))
            traceback.print_exc(file=sys.stdout)

    def set_config(self, config):
        self.config = config

    def get_data(self):
        return {
            'id': self.module_id,
            'name': self.module_name,
            'description': self.description,
            'config': self.config
        }

    async def print_data(self, args):
        await self.ws.send(message_utils.info(dumps(self.get_data(), indent=4)))


class FileIOModule(BaseModule):
    def __init__(self, ws, path, extensions, name='', description='', ):
        BaseModule.__init__(self, ws, name, description)
        self.path = path
        self.extensions = extensions
        self.index = 0
        self.add_command(Command('--search', ('-s', 'search'),
                                 ref_strings.module.help['--search']), self.search_file)
        self.add_command(Command('--list', ('-ls', 'list'),
                                 ref_strings.module.help['--list']), self.list_file)
        self.add_command(Command('--reload', ('-re', 'reload'),
                                 ref_strings.module.help['--reload']), self.reload)
        self.add_command(Command('--list-by-id', ('-lsi',), ref_strings.module.help['--list-by-id']),
                         self.list_file_by_id)
        self.get_file_list()

    def get_file_list(self):
        self.file_list = fileutils.listFile(self.path, self.extensions)

    async def list_file(self, args):
        page = 1
        if len(args) != 0:
            page = int(args[0])
        entries = message_utils.getPage(self.file_list, page)
        await message_utils.printEntries(self.ws, entries)

    async def list_file_by_id(self, args):
        page = 1
        if len(args) != 0:
            page = int(args[0]) // 10 + 1
        entries = message_utils.getPage(self.file_list, page)
        await message_utils.printEntries(self.ws, entries)

    async def search_file(self, args):
        if len(args) == 0:
            await self.ws.send(message_utils.error(ref_strings.search_error))
            return
        results = self.search(args)
        if len(results) == 0:
            await self.ws.send(message_utils.info(ref_strings.empty_result))
        else:
            string = '\n'
            for i in results:
                string += ref_strings.list_format.format(i[0], i[1])+'\n'
            await self.ws.send(
                message_utils.info(string))

    async def open_file(self, args):
        if len(args) == 0:
            return
        try:
            arg1 = int(args[0])
            if arg1 < len(self.file_list):
                if not os.path.exists(self.file_list[arg1]):
                    await self.reload(args)
                    return
                self.index = arg1
                await self.open(arg1)
            else:
                await self.ws.send(message_utils.error(ref_strings.file_not_exists))
        except ValueError:
            await self.ws.send(message_utils.error(ref_strings.invaild_id))
        except Exception as e:
            await self.ws.send(message_utils.error("Unexpected exception" + str(e)))

    async def open(self, index):
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
