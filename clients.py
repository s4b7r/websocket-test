from uuid import uuid4
from starlette.websockets import WebSocketDisconnect
import json
from channels import Channel


class Client:
    channel: Channel

    def __init__(self, websocket) -> None:
        self.sock = websocket

    @property
    def websocket(self):
        return self.sock

    async def init_id(self):
        self.id = str(uuid4())
        print(f'New {self}')
        await self.sock.send_json({'k': 'your_client_id', 'v': self.id})

    def __repr__(self):
        return f'client {self.id}'

    async def assign_channel(self, channel):
        self.channel = channel
        await channel.add_sock_to_channel(self)
        await self.sock.send_json({'k': 'your_channel_id', 'v': channel.get_channel_id()})
    
    async def receive_handler(self, msg):
        print(f'From {self} received {msg}')
        await self.sock.send_json({'k': 'ack', 'v': msg})
        msgj = msg if isinstance(msg, dict) else json.loads(msg)
        if msgj['k'] == 'my_choice':
            await self.channel.send_to_channel_json({'k': 'their_choice', 'v': {
                                                                                'their_client': self.id,
                                                                                'their_choice': msgj['v']
                                                                                }
                                                    })

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
