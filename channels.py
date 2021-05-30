import asyncio
from uuid import uuid4


class Channel:
    def __init__(self, channels_list):
        self.socks = []
        self.parent = channels_list

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
        send = self.send_to_channel(f'{websocket} left your channel')
        return asyncio.gather(close, send, return_exceptions=True)

    @staticmethod
    def get_new_channel(channels_list):
        channel = Channel(channels_list)
        channels_list[str(uuid4())] = channel
        return channel

    def get_channel_id(self):
        for id, chan in self.parent.items():
            if chan == self:
                return id
        raise RuntimeError(f'Did not find that channel in channels dict')

    def add_sock_to_channel(self, websocket):
        self.socks.append(websocket)
