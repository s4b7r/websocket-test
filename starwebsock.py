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
        function runWebsockets() {
            if ("WebSocket" in window) {
                var connection_id = String(prompt("connection_id?", ""));
                var ws = new WebSocket("ws://localhost:8000/ws/" + connection_id);
                ws.onopen = function() {
                    console.log("Sending websocket data with connection_id " + connection_id);
                    ws.send("Hello From Client");
                };
                ws.onmessage = function(e) { 
                    console.log(e.data);
                };
                ws.onclose = function() { 
                    console.log("Closing websocket connection");
                };
            } else {
                alert("WS not supported, sorry!");
            }
        }
    </script>
</head>
<body><a href="javascript:runWebsockets()">Say Hello From Client</a></body>
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
    _ = await websocket.receive_text()
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
    _ = await websocket.receive_text()
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
