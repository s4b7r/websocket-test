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

from channels import Channel


template = """\
<!DOCTYPE HTML>
<html>
<head>
    <script type = "text/javascript">


        const createSocket = (channel_url) => {
            const socket = new WebSocket(channel_url);
            
            socket.onopen = (event) => {
                document.getElementById('status').textContent = `Connected`;
            };
            socket.onmessage = (event) => {
                console.log(event.data);
                document.getElementById('channel_id').value = event.data;
            };
            socket.onclose = function() { 
                console.log("Closing websocket channel");
                document.getElementById('status').textContent = `Disconnected`;
            };

            window.addEventListener('unload', (event) => socket.close());

            return socket;
        }

        const disconnectSocket = (socket) => {
            socket.close();
            document.getElementById('status').textContent = `Disconnected`;
        };

        document.addEventListener("DOMContentLoaded", () => {
            let socket;

            const form = document.getElementById('connect_form');
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                if (socket) {
                    disconnectSocket(socket);
                }
                socket = createSocket("ws://localhost:8000/ws/" + String(document.getElementById('channel_id').value));;
            });

            const disconnectButton = document.getElementById('disconnect_button');
            disconnectButton.addEventListener('click', () => disconnectSocket(socket));
        });
    </script>
</head>
<body>
<a href="javascript:runWebsockets()">Say Hello From Client</a><br>
<h1>Status: <span id="status">Disconnected</span></h1>
<form id="connect_form">
    <input type="text" id="channel_id" placeholder="channel_id" style="width: 500px;" /><br>
    <button type="submit">Connect</button>
    <button type="button" id="disconnect_button">Disconnect</button>
</form>
</body>
</html>
"""


app = Starlette()

channels = {}


@app.route('/')
async def homepage(request):
    return HTMLResponse(Template(template).render())


@app.websocket_route('/ws/{channel_id}')
async def websocket_endpoint(websocket):
    channel_id = websocket.path_params.get('channel_id')
    channel = channels.get(channel_id)
    print(f'New {websocket} to {channel_id}')
    await websocket.accept()
    channel.add_sock_to_channel(websocket)
    await channel.send_to_channel(f'New {websocket} to channel {channel_id}')
    await sock_receive_loop(websocket, channel)


@app.websocket_route('/ws/')
async def websocket_endpoint(websocket):
    channel = Channel.get_new_channel(channels)
    channel_id = channel.get_channel_id()
    print(f'New channel {channel_id} from {websocket}')
    await websocket.accept()
    channel.add_sock_to_channel(websocket)
    await websocket.send_text(f'You are {websocket} with new channel {channel_id}')
    await sock_receive_loop(websocket, channel)


async def sock_receive_loop(websocket, channel):
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    await channel.remove_sock_from_channel(websocket)


if __name__ == '__main__':
    uvicorn.run('starwebsock:app', host='0.0.0.0', port=8000, reload=True)
