/**
 * The root function
 * @param {*} chat The chat object
 */
function init(chat) {
    createStartTime(chat);

    chat.messages.forEach(function parse(value) {
        createChatField(value);
    });

}

/**
 * Function to create start time element.
 * @param {*} chat The chat object
 */
function createStartTime(chat) {
    let startTime = document.getElementById('start_time');
    let time = "Chat log start from " + new Date(chat.time * 1000).toLocaleString();
    startTime.innerHTML = time;
}

function createChatField(message) {
    let span = document.getElementById('chat');

    let chatbox = document.createElement('div');

    if (message.is_host) {
        chatbox.setAttribute('class', 'chatbox-host');
    } else {
        chatbox.setAttribute('class', 'chatbox-non-host');
    }

    let time = createTime(message);
    chatbox.appendChild(time);

    let dialog = createDialog(message);
    chatbox.appendChild(dialog);

    span.appendChild(chatbox);

}

function createTime(message) {
    let time = document.createElement('div');
    time.setAttribute('class', 'time');
    let timeString = new Date(message.time * 1000).toLocaleString();
    let timeNode = document.createTextNode(timeString);
    time.appendChild(timeNode);
    return time;
}

function createDialog(message) {
    let dialog = document.createElement('div');
    dialog.setAttribute('class', 'dialog');

    let avatar = createAvatar(message);
    dialog.appendChild(avatar);

    let innerDialog = document.createElement('div');
    innerDialog.setAttribute('class', 'innerdialog');

    let sender = createSender(message);
    innerDialog.appendChild(sender);

    let msg = createMessage(message);
    innerDialog.appendChild(msg);

    dialog.appendChild(innerDialog);
    return dialog;
}

function createMessage(message) {
    let messageBox = document.createElement('div');
    messageBox.setAttribute('class', 'message');
    let messageString = message.message;
    let messageNode = document.createTextNode(messageString);
    messageBox.appendChild(messageNode);
    return messageBox;
}

function createSender(message) {
    let sender = document.createElement('div');
    sender.setAttribute('class', 'sender');
    let name = message.sender;
    let senderName = document.createTextNode(name);
    sender.appendChild(senderName);
    return sender;
}

function createAvatar(message) {
    let image = document.createElement('img');
    image.setAttribute('class', 'avatar');
    image.setAttribute('src', 'avatar/' + message.sender + '.png');
    return image;
}