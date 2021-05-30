import asyncio
from uuid import uuid4


class Channel:
    def __init__(self, channels_list, id=None):
        self.socks = []
        self.parent = channels_list
        self.id = id
        self.choice_pair = {}

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
    
    async def set_choice(self, client, choice):
        self.choice_pair[client] = choice
        await self.send_choice_pair_on_complete()

    async def send_choice_pair_on_complete(self):
        for client in self.socks:
            if client not in self.choice_pair:
                print(f'{client} not in channels choice pair')
                break
            print(f'{client} is in channels choice pair')
        else:
            for client in self.socks:
                print(f'sending choice pair to {client}')
                for other in self.socks:
                    if other != client:
                        break
                others_choice = self.choice_pair[other]
                print(f'partner of {client} is {other} with choice {others_choice}')
                await client.websocket.send_json({'k': 'their_choice', 'v': {
                                                                            'their_client': other.id,
                                                                            'their_choice': others_choice
                                                                            }
                                                })


class ChannelFullError(Exception):
    pass