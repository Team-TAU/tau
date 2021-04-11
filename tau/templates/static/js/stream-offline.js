const appendStreamOffline = (message) => {
    title = message.origin === 'test' ?
        `[Test] Stream Offline` :
        message.origin === 'replay' ?
            `[Replay] Stream Offline` :
            `Stream Offline`;
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}
