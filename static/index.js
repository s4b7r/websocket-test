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

const sendChoiceButton = (event, socket, label) => {
    event.preventDefault();

    for (const choice_label of Object.keys(choices)) {
        let choice = choices[choice_label];
        choice['a'].classList.add('locked_link');
        if (choice_label === label) choice['div'].classList.add('locked_choice_div')
        else choice['div'].classList.add('locked_nonchoice_div')
    }

    my_choice = label;
    sendChoice(socket);
}

var choices = {};

document.addEventListener("DOMContentLoaded", () => {
    choices['stone'] = {};
    choices['stone']['div'] = choice_div_stone = document.getElementById('choice_stone_div');
    choices['stone']['a'] = choice_div_stone = document.getElementById('choice_stone');
    choices['paper'] = {};
    choices['paper']['div'] = choice_div_paper = document.getElementById('choice_paper_div');
    choices['paper']['a'] = choice_div_paper = document.getElementById('choice_paper');
    choices['scissors'] = {};
    choices['scissors']['div'] = choice_div_scissors = document.getElementById('choice_scissors_div');
    choices['scissors']['a'] = choice_div_scissors = document.getElementById('choice_scissors');
    
    if (channel_id === "None") channel_id = '';
    if (client_id === "None") client_id = '';
    updateLinks();
    
    var socket;
    if (socket) {
        disconnectSocket(socket);
    }
    socket = createSocket("ws://localhost:8000/ws/" + channel_id + "/" + client_id);;
    
    choices['stone']['a'].addEventListener('click', (event) => sendChoiceButton(event, socket, 'stone'));
    choices['paper']['a'].addEventListener('click', (event) => sendChoiceButton(event, socket, 'paper'));
    choices['scissors']['a'].addEventListener('click', (event) => sendChoiceButton(event, socket, 'scissors'));
});
