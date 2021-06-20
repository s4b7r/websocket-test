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