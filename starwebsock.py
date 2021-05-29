# Original starlette.io WebSocket example was
# based on https://gist.github.com/s4b7r/21b52a8ca6e4ecc0154c1da605b376ac
# forked from https://gist.github.com/akiross/a423c4e8449645f2076c44a54488e973

from starlette.applications import Starlette
from starlette.responses import HTMLResponse
from starlette.websockets import WebSocket
from jinja2 import Template
import uvicorn


template = """\
<!DOCTYPE HTML>
<html>
<head>
    <script type = "text/javascript">
        function runWebsockets() {
            if ("WebSocket" in window) {
                var ws = new WebSocket("ws://localhost:8000/ws");
                ws.onopen = function() {
                    console.log("Sending websocket data");
                    ws.send("Hello From Client");
                };
                ws.onmessage = function(e) { 
                    alert(e.data);
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


@app.route('/')
async def homepage(request):
    return HTMLResponse(Template(template).render())


@app.websocket_route('/ws')
async def websocket_endpoint(websocket):
    await websocket.accept()
    # Process incoming messages
    while True:
        mesg = await websocket.receive_text()
        await websocket.send_text(mesg.replace("Client", "Server"))
    await websocket.close()


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)
