const channelRaidTest = () => {
    const form = document.getElementById('channel-raid-test');
    const eles = form.elements;
    const from_broadcaster_user_name = eles.namedItem('raid-from_broadcaster_user_name').value;
    const from_broadcaster_user_id = eles.namedItem('raid-from_broadcaster_user_id').value;

    const payload = {
        from_broadcaster_user_name,
        from_broadcaster_user_id: from_broadcaster_user_id,
        from_broadcaster_user_login: from_broadcaster_user_name.toLowerCase(),
        to_broadcaster_user_id: broadcaster_user_id,
        to_broadcaster_user_login: broadcaster_user_name.toLowerCase(),
        to_broadcaster_user_name: broadcaster_user_name,
        viewers: Number(eles.namedItem('viewers').value)
    }
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/twitch-events/channel-raid/test/`, payload).subscribe(resp => {
        console.log(resp);
    });
    return false;
}

const appendRaid = (message) => {
    const username = message.event_data.from_broadcaster_user_name;
    const viewers = message.event_data.viewers;
    title = message.origin === 'test' ? `[Test] ${username} raided with ${viewers} viewers.` :
        message.origin === 'replay' ? `[Replay] ${username} raided with ${viewers} viewers.` :
            `${username} raided with ${viewers} viewers.`
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}
