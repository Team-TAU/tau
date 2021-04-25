const appendStreamOnline = (message) => {
    title = message.origin === 'test' ?
        `[Test] Stream Online` :
        message.origin === 'replay' ?
            `[Replay] Stream Online` :
            `Stream Online`;
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}
