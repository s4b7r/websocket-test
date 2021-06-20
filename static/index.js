let channel_id;
let client_id;
let base_url;
let my_choice;

const updateLinks = () => {
    document.getElementById('channel_id').href = base_url + channel_id;
    document.getElementById('channel_id').innerText = base_url + channel_id;
    document.getElementById('your_client_id').href = base_url + channel_id + '/' + client_id;
    document.getElementById('your_client_id').innerText = base_url + channel_id + '/' + client_id;
};

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
            client_id = msg.v;
            updateLinks();
        } else if (msg.k ==="your_channel_id" ) {
            channel_id = msg.v;
            updateLinks();
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
    socket.send(JSON.stringify({'k': 'my_choice', 'v': my_choice}));
}

const sendChoiceButton = (label, socket) => {
    my_choice = label;
    sendChoice(socket);
}

document.addEventListener("DOMContentLoaded", () => {
    var socket;

    if (socket) {
        disconnectSocket(socket);
    }
    if (channel_id === "None") channel_id = '';
    if (client_id === "None") client_id = '';
    updateLinks();
    socket = createSocket("ws://localhost:8000/ws/" + channel_id + "/" + client_id);;
    
    const choiceLinkStone = document.getElementById('choice_stone');
    choiceLinkStone.addEventListener('click', (event) => {
        console.log(event);
        event.preventDefault();
        sendChoiceButton('stone', socket);
        });
    const choiceLinkPaper = document.getElementById('choice_paper');
    choiceLinkPaper.addEventListener('click', (event) => {
        console.log(event);
        event.preventDefault();
        sendChoiceButton('paper', socket);
        });
    const choiceLinkScissors = document.getElementById('choice_scissors');
    choiceLinkScissors.addEventListener('click', (event) => {
        console.log(event);
        event.preventDefault();
        sendChoiceButton('scissors', socket);
        });
});
