import asyncio
from uuid import uuid4


class Channel:
    def __init__(self, channels_list, id=None):
        self.socks = []
        self.parent = channels_list
        self.id = id

    async def send_to_channel_json(self, json):
        sends = []
        for ws in self.socks:
            sends.append(ws.websocket.send_json(json))
        return asyncio.gather(*sends)

    async def send_to_channel(self, text):
        return self.send_to_channel_text(text)

    async def send_to_channel_text(self, text):
        sends = []
        for ws in self.socks:
            sends.append(ws.websocket.send_text(text))
        return asyncio.gather(*sends)

    async def remove_sock_from_channel(self, websocket):
        self.socks.remove(websocket)

        if len(self.socks) == 0:
            del self.parent[self.id]
        
        close = websocket.websocket.close()
        send = self.send_to_channel(f'{websocket} left {self}')
        return asyncio.gather(close, send, return_exceptions=True)

    @staticmethod
    def get_new_channel(channels_list):
        id = str(uuid4())
        channel = Channel(channels_list, id=id)
        channels_list[id] = channel
        print(f'New {channel}')
        return channel

    def get_channel_id(self):
        return self.id

    async def add_sock_to_channel(self, websocket):
        if len(self.socks) >= 2:
            raise ChannelFullError()

        self.socks.append(websocket)
        print(f'{self} got new {websocket}')
        await self.send_to_channel_json({'k': 'client_joined_channel', 'v': websocket.to_json()})

    def __repr__(self) -> str:
        return f'channel {self.id}'


class ChannelFullError(Exception):
    pass