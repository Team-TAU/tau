

const channelPointsRedemptionTest = () => {
    const form = document.getElementById('channel-points-redemption-test');
    const eles = form.elements;
    const user_name = eles.namedItem('username').value;
    const user_input = eles.namedItem('user_input').value;
    const status = 'unfilled';
    const redeemed_at = new Date().toISOString();
    const id = "649995ea-b88b-446d-a011-0cc183588bd4"; // TODO: Generate UUID
    console.log(eles.namedItem('reward').value);
    const reward_data = rewards[eles.namedItem('reward').value];
    reward = {
        id: reward_data.id,
        title: reward_data.title,
        prompt: reward_data.prompt,
        cost: reward_data.cost
    };

    const payload = {
        broadcaster_user_id,
        broadcaster_user_name,
        broadcaster_user_login: broadcaster_user_name.toLowerCase(),
        id,
        user_name,
        user_id: 1234,
        user_login: user_name.toLowerCase(),
        user_input,
        status,
        redeemed_at,
        reward
    };
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/twitch-events/channel-channel_points_custom_reward_redemption-add/test/`, payload).subscribe(resp => {
        console.log(resp);
    });
    console.log(rewards);
    return false;
}

const appendPointsRedemption = (message) => {
    const username = message.event_data.user_name;
    const reward_name = message.event_data.reward.title;
    title = message.origin === 'test' ? `[Test] ${username} Redeemed ${reward_name}.` :
        message.origin === 'replay' ? `[Replay] ${username} Redeemed ${reward_name}.` :
            `${username} Redeemed ${reward_name}.`
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}

const buildRedemptionSelect = () => {
    const select = document.getElementById('reward');
    const showDisabledBox = document.getElementById('show-disabled');
    const showDisabled = showDisabledBox.checked;
    select.innerHTML = '';
    options = '';
    let i = 0;
    rewards.filter((row) => {
        return showDisabled || row.is_enabled
    }).forEach(row => {
        options += `<option value="${i}">${row.title}</option>`;
        console.log(row.title);
        i += 1;
    });
    select.innerHTML = options;
}
