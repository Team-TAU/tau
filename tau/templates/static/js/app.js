let rewards = [];
let eventSubList = [];
const port = window.location.port ? `:${window.location.port}` : '';
const host = window.location.hostname;
const protocol = window.location.protocol;
const socketProtocol = protocol === 'https:' ? 'wss:' : 'ws:';

const testModals = {
    "channel-follow": "#testFollowModal",
    "channel-update": "#testUpdateModal",
    "channel-raid": "#testRaidModal",
    "channel-cheer": "#testCheersModal",
    "channel-channel_points_custom_reward_redemption-add": "#testPointsRedemptionModal",
}

// Once the window/scripts/etc. have all been loaded, set up our json and text websockets.
function twitchEventsWebsocket() {
    console.log('Setup twitch events!');
    setupJsonWebsocket(`${socketProtocol}//${host}${port}/ws/twitch-events/`, handleEventMessage);

    const tokenModal = document.getElementById('tokenModal');
    tokenModal.addEventListener('shown.bs.modal', function () {
        ajaxGet(`${protocol}//${host}${port}/api/v1/tau-user-token/`).subscribe(resp => {
            const token = resp.token;
            document.getElementById('token').value = token;
        });
    });
}

/**
 * Sets up a subscribed RxJS webSocketSubject that connects to the server's JSON widgets websocket
 * channel.  This example uses RxJS' retryWhen operator to attempt reconnection if the websocket
 * disconnects.  Data returned from the server is json, and is (by default) deserialized into a
 * javascript object, which is then used to populate the RxJS json card alerts.  The openObserver
 * parameter is also set to update a status element, showing the user the websocket connection status
 */
const setupJsonWebsocket = (url, handler) => {
    // Loading webSocket, retryWhen, and delay from rxjs.
    const webSocket = rxjs.webSocket.webSocket;
    const retryWhen = rxjs.operators.retryWhen;
    const delay = rxjs.operators.delay;

    try {
        // Create a webSocket subject, connecting to the ws widgets/json endpoint.
        const jsonSubject = webSocket({
            url,
            openObserver: {
                next: () => {
                    console.log(`Connected to websocket at ${url}`)
                }
            },
        });

        // Add a reconnect if connection dies using rxjs' subject pipe operator
        // then subscribe to any messages received by the subject.
        jsonSubject.pipe(
            // If we are disconnected, wait 5000ms before attempting to reconnect.
            retryWhen((err) => {
                console.log("Disconnected!  Attempting reconnection shortly...")
                return err.pipe(delay(2000));
            })
        ).subscribe(
            // Once we receieve a message from the server, pass it to the handler function.
            msg => {
                handler(msg);
            },
        );
    } catch (err) {
        console.log(err);
    }
}

function loadEventSubSubscriptions() {
    ajaxGet(`${protocol}//${host}${port}/api/v1/twitch/eventsub-subscriptions?active=true`).subscribe(res => {
        eventSubList = res;
        const tbody = document.getElementById('events-body');
        let html = '';
        res.forEach(row => {
            const event = row.subscription_type;
            const status = '<i class="bi bi-check2 text-success"></i>';
            const test = row.lookup_name in testModals ? 
                `<a href='#' class="text-decoration-none pe-2" data-bs-toggle="modal" data-bs-target="${testModals[row.lookup_name]}"><i class="bi bi-pencil-square"></i></a>` :
                '';
            html += `<tr id="${row.id}"><th scope="row">${event}</th><td class="text-center">${status}</td><td>${test}</td></tr>`
        });
        tbody.innerHTML = html;
    });
}

function eventTitle(event) {
    switch(event.event_type) {
        case "channel-follow":
            return `${event.event_data.user_name} followed.`;
        case "channel-cheer":
            return `${event.event_data.user_name} cheered ${event.event_data.bits} bits.`;
        case "channel-raid":
            return `${event.event_data.from_broadcaster_user_name} raided with ${event.event_data.viewers} viewers.`;
        case "channel-channel_points_custom_reward_redemption-add":
            const username = event.event_data.user_name;
            const reward_name = event.event_data.reward.title;
            return `${username} redeemed ${reward_name}.`;
        case "channel-subscribe":
            if (event.event_data.is_gift) {
                return `${event.event_data.user_name} received a gift sub.`
            } else {
                return `${event.event_data.user_name} subscribed.`
            }
        case "channel-subscription-gift":
            return `${event.event_data.user_name} gifted ${event.event_data.total} subs.`

    }
    event_type = eventSubList.find(ev => ev.lookup_name === event.event_type);
    return event_type.subscription_type;
}

const handleStatusMessage = (message) => {
    // message.forEach(row => {
    //     setStatus(row.event_type, row.new_value);
    // });
}

const handleEventMessage = (message) => {
    const titleText = eventTitle(message);
    title = message.origin === 'test' ?
        `[Test] ${titleText}` :
        message.origin === 'replay' ?
            `[Replay] ${titleText}` :
            titleText;
    replay = message.origin !== 'test' ?
        `<button class='btn btn-sm btn-primary' onclick='replayEvent("${message.id}")'>Replay</button>` :
        null;
    payload = eventTemplate(title, message, replay);
    const ele = document.getElementById('ws-accordion');
    ele.innerHTML = payload + ele.innerHTML;
    Prism.highlightAll();
}


const setStatus = (id, value) => {
    const ele = document.getElementById(id);
    if (value === 'CONNECTED') {
        ele.innerHTML = '<i class="bi bi-check2 text-success"></i>'
    } else if (value === 'CONNECTING') {
        ele.innerHTML = `<div class="spinner-border spinner-border-sm" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>`;
    } else {
        ele.innerHTML = '<i class="bi bi-x text-danger"></i>';
    }
}

const ajaxPut = (url, body) => {
    const ajax = rxjs.ajax.ajax;
    const of = rxjs.of;
    const map = rxjs.operators.map;
    const catchError = rxjs.operators.catchError;
    const csrftoken = Cookies.get('csrftoken');
    return ajax({
        url: url,
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body
    }).pipe(
        map(res => res.response),
        catchError(error => {
            console.log('error: ', error);
            return of(error);
        })
    );
}

const ajaxPost = (url, body) => {
    const ajax = rxjs.ajax.ajax;
    const of = rxjs.of;
    const map = rxjs.operators.map;
    const catchError = rxjs.operators.catchError;
    const csrftoken = Cookies.get('csrftoken');
    return ajax({
        url: url,
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body
    }).pipe(
        map(res => res.response),
        catchError(error => {
            console.log('error: ', error);
            return of(error);
        })
    );
}

const ajaxGet = (url) => {
    const ajax = rxjs.ajax.ajax;
    const of = rxjs.of;
    const map = rxjs.operators.map;
    const catchError = rxjs.operators.catchError;
    const csrftoken = Cookies.get('csrftoken');
    return ajax({
        url: url,
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        }
    }).pipe(
        map(res => res.response),
        catchError(error => {
            console.log('error: ', error);
            return of(error);
        })
    );
}

const eventTemplate = (title, eventObj, replay = null) => {
    const id = Math.random().toString(36).replace(/[^a-z]+/g, '').substr(0, 5);
    const eventStr = JSON.stringify(eventObj, null, 2);
    const replayStr = replay ? replay : '';
    return `
<div class="accordion-item">
    <h2 class="accordion-header" id="h-${id}">
      <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#id-${id}" aria-expanded="false" aria-controls="id-${id}">
        <div class="text-truncate" style="margin-right: 15px;">${title}</div>
      </button>
    </h2>
    <div id="id-${id}" class="accordion-collapse collapse" aria-labelledby="h-${id}" data-bs-parent="#ws-accordion">
      <div class="accordion-body">
          <pre><code class="language-json" style="font-size: 12px">${eventStr}</code></pre>
          ${replay ? replay : ''}
      </div>
    </div>
</div>`;
}

const replayEvent = (id) => {
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/twitch-events/${id}/replay/`, {}).subscribe(resp => {
        console.log(resp);
    })
}

const getUserId = (username_id, userid_id) => {
    const username = document.getElementById(username_id).value;
    const sub = ajaxGet(`${protocol}//${host}${port}/api/twitch/helix/users?login=${username}`).subscribe(resp => {
        if (resp.data.length > 0) {
            document.getElementById(userid_id).value = resp.data[0].id
        }
    });
}


const toggleVisibility = (ele) => {
    ele = $(ele);
    const i = $(ele.children()[0]);
    i.toggleClass('bi-eye');
    i.toggleClass('bi-eye-slash');
    const input = $(ele.siblings()[0]);
    const inputType = input.prop('type') === 'password' ? 'text' : 'password';
    input.prop('type', inputType);
}
