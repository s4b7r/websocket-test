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

const processTheirChoice = (their_choice) => {
    for (const choice_label of Object.keys(their_choices)) {
        let choice = their_choices[choice_label];
        choice['a'].classList.add('locked_link');
        if (choice_label === their_choice) choice['div'].classList.add('locked_choice_div')
        else choice['div'].classList.add('locked_nonchoice_div')
    }
}

const createSocket = (channel_url) => {
    const socket = new WebSocket(channel_url);
    
    socket.onopen = (event) => {
        document.getElementById('status').textContent = `Connected`;
    };
    socket.onmessage = (event) => {
        console.log(event.data);
        var msg = JSON.parse(event.data);
        if (msg.k === "your_client_id") {
            client_id = msg.v;
            updateLinks();
        } else if (msg.k ==="your_channel_id" ) {
            channel_id = msg.v;
            updateLinks();
        } else if (msg.k === "their_choice") {
            processTheirChoice(msg.v.their_choice);
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
var their_choices = {};

document.addEventListener("DOMContentLoaded", () => {
    choices['stone'] = {};
    choices['stone']['div'] = document.getElementById('choice_stone_div');
    choices['stone']['a'] = document.getElementById('choice_stone');
    choices['paper'] = {};
    choices['paper']['div'] = document.getElementById('choice_paper_div');
    choices['paper']['a'] = document.getElementById('choice_paper');
    choices['scissors'] = {};
    choices['scissors']['div'] =  document.getElementById('choice_scissors_div');
    choices['scissors']['a'] =  document.getElementById('choice_scissors');
    
    their_choices['stone'] = {};
    their_choices['stone']['div'] = document.getElementById('their_choice_stone_div');
    their_choices['stone']['a'] = their_choices['stone']['div'].childNodes[1];
    console.log(their_choices['stone']['a']);
    their_choices['paper'] = {};
    their_choices['paper']['div']  = document.getElementById('their_choice_paper_div');
    their_choices['paper']['a'] = their_choices['paper']['div'].childNodes[1];
    their_choices['scissors'] = {};
    their_choices['scissors']['div'] = document.getElementById('their_choice_scissors_div');
    their_choices['scissors']['a'] = their_choices['scissors']['div'].childNodes[1];
    
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
