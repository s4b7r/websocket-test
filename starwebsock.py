# Original starlette.io WebSocket example was
# based on https://gist.github.com/s4b7r/21b52a8ca6e4ecc0154c1da605b376ac
# forked from https://gist.github.com/akiross/a423c4e8449645f2076c44a54488e973

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket, WebSocketDisconnect
from jinja2 import Template
import uvicorn


template = """\
<!DOCTYPE HTML>
<html>
<head>
    <script type = "text/javascript">
        function runWebsockets() {
            if ("WebSocket" in window) {
                var connection_id = String(prompt("connection_id?", "nope"));
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
    await websocket.accept()
    _ = await websocket.receive_text()
    connections[connection_id] = websocket
    for ws in connections.values():
        print(f'waiting for {ws}...')
        await ws.send_text(f'New connection to server with id {connection_id}')
        print('fin wait')
    print(connections)
    try:
        while True:
            _ = await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    del connections[connection_id]
    await websocket.close()


if __name__ == '__main__':
    uvicorn.run('starwebsock:app', host='0.0.0.0', port=8000, reload=True)
