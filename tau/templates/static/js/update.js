// TODO: Dropdown of twitch categories and corresponding ids.
// TODO: Dropdown of available languages

const channelUpdateTest = () => {
    const form = document.getElementById('channel-update-test');
    const eles = form.elements;

    const data = {
        title: eles.namedItem('title').value,
        language: 'en',
        is_mature: eles.namedItem('is_mature').checked,
        category_id: 12345,
        category_name: eles.namedItem('category_name').value,
        broadcaster_user_id,
        broadcaster_user_name,
        broadcaster_user_login: broadcaster_user_name.toLowerCase()
    }
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/twitch-events/channel-update/test/`, data).subscribe(resp => {
        console.log(resp);
    });
    return false;
}

const appendUpdate = (message) => {
    title = message.origin === 'test' ?
        `[Test] Stream Updated` :
        message.origin === 'replay' ?
            `[Replay] Stream Updated` :
            `Stream Updated`;
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}
