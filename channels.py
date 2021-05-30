import asyncio
from uuid import uuid4


class Channel:
    def __init__(self, channels_list, id=None):
        self.socks = []
        self.parent = channels_list
        self.id = id

    async def send_to_channel(self, text):
        sends = []
        for ws in self.socks:
            sends.append(ws.send_text(text))
        return asyncio.gather(*sends)

    async def remove_sock_from_channel(self, websocket):
        self.socks.remove(websocket)

        if len(self.socks) == 0:
            for chanid, chan in self.parent.items():
                if chan == self:
                    break
            else:
                raise RuntimeError()
            del self.parent[chanid]
        
        close = websocket.close()
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

    def add_sock_to_channel(self, websocket):
        self.socks.append(websocket)
        print(f'{self} got new {websocket}')

    def __repr__(self) -> str:
        return f'channel {self.id}'
