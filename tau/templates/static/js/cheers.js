const channelCheerTest = () => {
    const form = document.getElementById('channel-cheer-test');
    const eles = form.elements;
    is_anonymous = eles.namedItem('is_anonymous').checked;
    user_name = eles.namedItem('cheer-username').value;
    user_id = eles.namedItem('cheer-user-id').value;

    const payload = {
        is_anonymous,
        user_id: !is_anonymous ? user_id : null,
        user_name: !is_anonymous ? user_name : null,
        user_login: !is_anonymous ? user_name.toLowerCase() : null,
        broadcaster_user_id,
        broadcaster_user_name,
        broadcaster_user_login: broadcaster_user_name.toLowerCase(),
        bits: Number(eles.namedItem('bits').value),
        message: eles.namedItem('cheer-message').value
    }
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/twitch-events/channel-cheer/test/`, payload).subscribe(resp => {
        console.log(resp);
    });
    return false;
}

const appendCheer = (message) => {
    const username = message.event_data.is_anonymous ? 'Anonymous' : message.event_data.user_name;
    title = message.origin === 'test' ?
        `[Test] ${username} Cheered ${message.event_data.bits} bits` :
        message.origin === 'replay' ?
            `[replay] ${username} Cheered ${message.event_data.bits} bits` :
            `${username} Cheered ${message.event_data.bits} bits`;
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}
