const channelFollowTest = () => {
    const form = document.getElementById('channel-follow-test');
    const eles = form.elements;
    const user_name = eles.namedItem('follow-username').value
    const user_id = eles.namedItem('follow-user-id').value
    const payload = {
        user_name,
        user_id,
        user_login: user_name.toLowerCase(),
        broadcaster_user_id,
        broadcaster_user_name,
        broadcaster_user_login: broadcaster_user_name.toLowerCase(),
    };
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/twitch-events/channel-follow/test/`, payload).subscribe(resp => {
        console.log(resp);
    });
    return false;
}

const appendFollow = (message) => {
    const username = message.event_data.user_name;
    title = message.origin === 'test' ? `[Test] ${username} Followed.` :
        message.origin === 'replay' ? `[Replay] ${username} Followed.` :
            `${username} Followed.`
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}
