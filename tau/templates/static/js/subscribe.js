const channelSubscribeTest = () => {
    const form = document.getElementById('channel-sub-test');
    const eles = form.elements;
    const user_name = eles.namedItem('sub-username').value;
    const user_id = eles.namedItem('sub-user-id').value;
    const tier = eles.namedItem('tier').value;
    const message = eles.namedItem('sub-message').value;
    const cumulative_months = eles.namedItem('cumulative_months').value;
    const streak_months = eles.namedItem('streak_months').value;

    const payloadData = {
        topic: `channel-subscribe-events-v1.${broadcaster_user_id}`,
        message: {
            "benefit_end_month": 0,
            "user_name": user_name.toLowerCase(),
            "display_name": user_name,
            "channel_name": broadcaster_user_name.toLowerCase(),
            "user_id": user_id,
            "channel_id": broadcaster_user_id,
            "time": new Date().toISOString(),
            "sub_message": {
                "message": message,
                "emotes": null
            },
            "sub_plan": tier,
            "sub_plan_name": `Channel Subscription (${broadcaster_user_name.toLowerCase()})`,
            "months": 0,
            "cumulative_months": Number(cumulative_months),
            "context": cumulative_months === 0 ? "sub" : "resub",
            "is_gift": false,
            "multi_month_duration": 0
        }
    }
    if(Number(streak_months) > 0) {
        payloadData.message.streak_months=Number(streak_months)
    }

    const payload = {data: payloadData, 'type': 'MESSAGE'};
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/twitch-events/subscribe/test/`, payload).subscribe(resp => {
        console.log(resp);
    });
    return false;
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
    const data = message.event_data.data.message;
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
    const data = message.event_data.data.message;
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
