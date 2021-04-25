const channelSubscribeTest = () => {
    const form = document.getElementById('channel-sub-test');
    const eles = form.elements;
    const user_name = eles.namedItem('sub-username').value;
    const user_id = eles.namedItem('sub-user-id').value;
    const tier = eles.namedItem('tier').value;
    const message = eles.namedItem('message').value;
    const cumulative_months = eles.namedItem('cumulative_months').value;
    const streak_months = eles.namedItem('streak_months').value;

    const payload = {
        type: "MESSAGE",
        data: {
            topic: "channel-subscribe-events-v1.44322889",
            message: {
                "user_name": user_name.toLowerCase(),
                "display_name": user_name,
                "channel_name": broadcaster_user_name,
                "user_id": user_id,
                "channel_id": broadcaster_user_id,
                "time": new Date().toISOString(),
                "sub_plan": tier,
                "sub_plan_name": "Channel Subscription",
                "cumulative_months": cumulative_months,
                "streak_months": streak_months,
                "context": cumulative_months === 0 ? "sub" : "resub",
                "is_gift": false,
                "sub_message": {
                    "message": message,
                    "emotes": []
                }
            }
        }
    }
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/twitch-events/subscribe/test/`, payload).subscribe(resp => {
        console.log(resp);
    });
    return false;
}

const appendSubscribe = (message) => {
    console.log('appendSubscribe', message);
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
