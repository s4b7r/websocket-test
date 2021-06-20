# Original starlette.io WebSocket example was
# based on https://gist.github.com/s4b7r/21b52a8ca6e4ecc0154c1da605b376ac
# forked from https://gist.github.com/akiross/a423c4e8449645f2076c44a54488e973


from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from jinja2 import Template
import uvicorn
from uuid import uuid4
import asyncio
import starlette
from starlette.templating import Jinja2Templates
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from channels import Channel
from clients import Client


channels = {}

templates = Jinja2Templates(directory='templates')
routes = [
        # Route('/', endpoint=homepage),
        Mount('/static', app=StaticFiles(directory='static'), name="static"),
        ]
app = Starlette(routes=routes)


@app.route('/')
async def homepage(request):
    return templates.TemplateResponse('index.html', {'request': request})


def get_existing_or_new_channel(channel_id):
    try:
        channel = channels[channel_id]
    except KeyError:
        channel = incoming_connection_creates_new_channel(channels)
    return channel


@app.websocket_route('/ws/{channel_id}/{client_id}')
async def websocket_endpoint(websocket):
    known_id = websocket.path_params.get('client_id')
    client = await client_init(websocket, known_id)

    channel_id = websocket.path_params.get('channel_id')
    channel = get_existing_or_new_channel(channel_id)

    await client.assign_channel(channel)
    await client.receive_loop()


def incoming_connection_creates_new_channel(channel_id):
    return Channel.get_new_channel(channel_id)


@app.websocket_route('/ws/{channel_id}/')
async def websocket_endpoint(websocket):
    client = await client_init(websocket)

    channel_id = websocket.path_params.get('channel_id')
    channel = get_existing_or_new_channel(channel_id)

    await client.assign_channel(channel)
    await client.receive_loop()


@app.websocket_route('/ws//')
async def websocket_endpoint(websocket):
    client = await client_init(websocket)
    
    channel = incoming_connection_creates_new_channel(channels)

    await client.assign_channel(channel)
    await client.receive_loop()


async def client_init(websocket, known_id=None):
    await websocket.accept()
    client = Client(websocket)
    await client.init_id(id=known_id)
    return client


if __name__ == '__main__':
    uvicorn.run('starwebsock:app', host='0.0.0.0', port=8000, reload=True)
