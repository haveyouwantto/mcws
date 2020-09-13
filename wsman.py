class WsManager:
    def __init__(self, ws):
        self.ws = ws
        self.uuids = set()

    async def submit(self, content):
        await self.ws.send(content)