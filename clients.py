from uuid import uuid4


class Client:
    def __init__(self, websocket) -> None:
        self.sock = websocket

    async def init_id(self):
        self.id = str(uuid4())
        print(f'New {self}')
        await self.sock.send_json({'k': 'your_client_id', 'v': self.id})

    def __repr__(self):
        return f'client {self.id}'

    async def assign_channel(self, channel):
        self.channel = channel
        await self.sock.send_json({'k': 'your_channel_id', 'v': channel.get_channel_id()})
    