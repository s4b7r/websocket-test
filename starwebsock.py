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
from clients import Client


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
                document.getElementById('last_message').value = event.data;
                var msg = JSON.parse(event.data);
                if (msg.k === "your_client_id") {
                    document.getElementById('your_client_id').value = msg.v;
                } else if (msg.k ==="your_channel_id" ) {
                    document.getElementById('channel_id').value = msg.v;
                } else if (msg.k === "their_choice") {
                    document.getElementById('their_choice').value = msg.v.their_choice;
                } else if (msg.k === "channel_full") {
                    document.getElementById('channel_id').value = "CHANNEL FULL";
                    socket.close()
                    document.getElementById('status').textContent = `Disconnected`;
                }
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

        const sendChoice = (socket) => {
            var my_choice = document.getElementById('your_choice').value;
            socket.send(JSON.stringify({'k': 'my_choice', 'v': my_choice}));
        }

        document.addEventListener("DOMContentLoaded", () => {
            let socket;

            const form = document.getElementById('connect_form');
            form.addEventListener('submit', (event) => {
                event.preventDefault();
                if (socket) {
                    disconnectSocket(socket);
                }
                var channel_id = String(document.getElementById('channel_id').value);
                var client_id = String(document.getElementById('your_client_id').value);
                socket = createSocket("ws://localhost:8000/ws/" + channel_id + "/" + client_id);;
            });
            const sendChoiceButton = document.getElementById('send_choice');
            sendChoiceButton.addEventListener('click', () => sendChoice(socket));

            const disconnectButton = document.getElementById('disconnect_button');
            disconnectButton.addEventListener('click', () => disconnectSocket(socket));
        });
    </script>
</head>
<body>
<h1>Status: <span id="status">Disconnected</span></h1>
<form id="connect_form">
    <input type="text" id="channel_id" placeholder="channel_id" style="width: 500px;" /><br>
    <input type="text" id="your_client_id" placeholder="client id" style="width: 500px;" /><br>
    <input type="text" id="your_choice" placeholder="your choice" style="width: 500px;" /><br>
    <input type="text" id="their_choice" placeholder="<their choice>" readonly style="width: 500px;" /><br>
    <input type="text" id="last_message" placeholder="<last message>" readonly style="width: 500px;" /><br>
    <button type="submit">Connect</button>
    <button type="button" id="disconnect_button">Disconnect</button>
    <button type="button" id="send_choice">Send choice</button>
</form>
</body>
</html>
"""


app = Starlette()

channels = {}


@app.route('/')
async def homepage(request):
    return HTMLResponse(Template(template).render())


@app.websocket_route('/ws/{channel_id}/{client_id}')
async def websocket_endpoint(websocket):
    known_id = websocket.path_params.get('client_id')
    client = await client_init(websocket, known_id)

    channel_id = websocket.path_params.get('channel_id')
    channel = channels.get(channel_id)

    await client.assign_channel(channel)
    await client.receive_loop()


@app.websocket_route('/ws/{channel_id}/')
async def websocket_endpoint(websocket):
    client = await client_init(websocket)

    channel_id = websocket.path_params.get('channel_id')
    channel = channels.get(channel_id)

    await client.assign_channel(channel)
    await client.receive_loop()


@app.websocket_route('/ws//')
async def websocket_endpoint(websocket):
    client = await client_init(websocket)
    
    channel = Channel.get_new_channel(channels)

    await client.assign_channel(channel)
    await client.receive_loop()


async def client_init(websocket, known_id=None):
    await websocket.accept()
    client = Client(websocket)
    await client.init_id(id=known_id)
    return client


if __name__ == '__main__':
    uvicorn.run('starwebsock:app', host='0.0.0.0', port=8000, reload=True)
