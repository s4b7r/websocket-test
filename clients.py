from uuid import uuid4
from starlette.websockets import WebSocketDisconnect
import json
import warnings

from channels import Channel, ChannelFullError


class Client:
    channel: Channel

    def __init__(self, websocket) -> None:
        self.sock = websocket

    @property
    def websocket(self):
        return self.sock

    def init_id(self, id=None):
        if id is not None:
            return self.init_known_id(id)
        if id is None:
            return self.init_new_id()
        raise RuntimeError('How did that happen!?')
    
    def init_new_id(self):
        id = str(uuid4())
        return self.init_known_id(id)

    async def init_known_id(self, id):
        self.id = id
        print(f'New {self}')
        await self.sock.send_json({'k': 'your_client_id', 'v': self.id})

    def __repr__(self):
        return f'client {self.id}'

    async def assign_channel(self, channel):
        self.channel = channel
        try:
            await channel.add_sock_to_channel(self)
            await self.sock.send_json({'k': 'your_channel_id', 'v': channel.get_channel_id()})
        except ChannelFullError:
            await self.sock.send_json({'k': 'channel_full', 'v': self.id})
    
    async def handle_my_choice(self, msgj):
        print(f'handling choice of {self}')
        await self.channel.set_choice(self, msgj['v'])

    async def receive_handler(self, msg):
        print(f'From {self} received {msg}')
        await self.sock.send_json({'k': 'ack', 'v': msg})
        msgj = msg if isinstance(msg, dict) else json.loads(msg)
        if msgj['k'] == 'my_choice':
            return await self.handle_my_choice(msgj)

    async def receive_loop(self):
        while True:
            try:
                msg = await self.sock.receive_json()
            except WebSocketDisconnect:
                break
            await self.receive_handler(msg)
        await self.channel.remove_sock_from_channel(self)

    def to_json(self):
        return self.id
