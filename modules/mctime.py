from modules.__init__ import BaseModule, Command


class MCTime(BaseModule):
    def __init__(self, ws):
        BaseModule.__init__(self, ws)
        self.add_command(Command('', None), self.print_time)

    async def print_time(self, args):
        await self.ws.send('')
