# Original starlette.io WebSocket example was
# based on https://gist.github.com/s4b7r/21b52a8ca6e4ecc0154c1da605b376ac
# forked from https://gist.github.com/akiross/a423c4e8449645f2076c44a54488e973


from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from jinja2 import Template
import uvicorn
from uuid import uuid4


template = """\
<!DOCTYPE HTML>
<html>
<head>
    <script type = "text/javascript">


        const createSocket = (connection_url) => {
            const socket = new WebSocket(connection_url);
            
            socket.onopen = (event) => {
                document.getElementById('status').textContent = `Connected`;
            };
            socket.onmessage = (event) => {
                console.log(event.data);
                document.getElementById('connection_id').value = event.data;
            };
            socket.onclose = function() { 
                console.log("Closing websocket connection");
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
                socket = createSocket("ws://localhost:8000/ws/" + String(document.getElementById('connection_id').value));;
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
    <input type="text" id="connection_id" placeholder="connection_id" style="width: 500px;" /><br>
    <button type="submit">Connect</button>
    <button type="button" id="disconnect_button">Disconnect</button>
</form>
</body>
</html>
"""


app = Starlette()

connections = {}


@app.route('/')
async def homepage(request):
    return HTMLResponse(Template(template).render())


@app.websocket_route('/ws/{connection_id}')
async def websocket_endpoint(websocket):
    connection_id = websocket.path_params.get('connection_id')
    print(f'New {websocket} to {connection_id}')
    await websocket.accept()
    connection = connections.get(connection_id)
    connection.append(websocket)
    for ws in connection:
        await ws.send_text(f'New {websocket} to connection {connection_id}')
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    connection.remove(websocket)
    if len(connection) == 0:
        del connections[connection_id]
    await websocket.close()


@app.websocket_route('/ws/')
async def websocket_endpoint(websocket):
    connection_id = str(uuid4())
    print(f'New connection {connection_id} from {websocket}')
    await websocket.accept()
    connection = [websocket]
    connections[connection_id] = connection
    await websocket.send_text(f'You are {websocket} with new connection {connection_id}')
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    connection.remove(websocket)
    if len(connection) == 0:
        del connections[connection_id]
    await websocket.close()


if __name__ == '__main__':
    uvicorn.run('starwebsock:app', host='0.0.0.0', port=8000, reload=True)
