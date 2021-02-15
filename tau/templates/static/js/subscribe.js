const channelSubscribeTest = () => {
    // TODO: Implement Sub Test
}

const appendSubscribe = (message) => {
    if (message.event_data.data.message.is_gift) {
        appendGiftSub(message);
    } else {
        appendSub(message);
    }
}

const appendGiftSub = (message) => {
    const origin = message.origin;
    const data = message.data.message;
    const username = data.display_name;
    const recipient = data.recipient_display_name;
    const prefix = origin === 'test' ? '[Test] ' :
        origin === 'replay' ? '[Replay] ' :
            '';
    const title = `${prefix}${username} gifted ${recipient} a sub.`;
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}

const appendSub = (message) => {
    const origin = message.origin;
    const data = message.data.message;
    const username = data.display_name;
    const prefix = origin === 'test' ? '[Test] ' :
        origin === 'replay' ? '[Replay] ' :
            '';
    const title = `${prefix}${username} Subscribed.`
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}
