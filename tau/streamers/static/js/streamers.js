let streamers = [];

window.onload = (event) => {
    ajaxGet(`${protocol}//${host}${port}/api/v1/streamers/`).subscribe(resp => {
        streamers = resp;
        updateStreamerList();
    });
    twitchEventsWebsocket();
    setupJsonWebsocket(`${socketProtocol}//${host}${port}/ws/twitch-events/`, handleStreamerNotification);
}

const handleStreamerNotification = (message) => {
    let broadcaster_id = null;
    let index = -1;
    switch (message.event_type) {
        case 'stream-offline':
            broadcaster_id = message.event_data.broadcaster_user_id;
            index = streamers.findIndex(streamer => streamer.twitch_id === broadcaster_id);
            if (index >= 0) {
                streamers[index].streaming = false;
            }
            updateStreamerList();
            break;
        case 'stream-online':
            broadcaster_id = message.event_data.broadcaster_user_id;
            index = streamers.findIndex(streamer => streamer.twitch_id === broadcaster_id);
            if(index >= 0) {
                streamers[index].streaming = true;
            }
            updateStreamerList();
            break;
    }
}

function submitAddStreamer() {
    const form = document.getElementById('add-streamer');
    const eles = form.elements;
    twitch_username = eles.namedItem('add-streamer-channel_name').value;

    const payload = {
        twitch_username
    }
    const sub = ajaxPost(`${protocol}//${host}${port}/api/v1/streamers/`, payload).subscribe(resp => {
        streamers.push(resp);
        console.log(streamers);
    });
    return false;
}

function updateStreamerList() {
    let html = '';
    streamers.forEach(streamer => {
        html += streamerListItem(streamer);
    });
    document.getElementById('streamer-list-body').innerHTML=html;
}

function streamerListItem(streamer) {
    const icon = streamer.streaming ? 'bi-camera-video-fill' : 'bi-camera-video-off-fill';
    const color = streamer.streaming ? 'red' : 'grey';
    return `<tr>
                <td class='text-center'><i class="bi ${icon}" style="color: ${color}"></i></td>
                <td>${streamer.twitch_username}</td>
                <td class= "text-end pe-2">
                    <div class="form-check form-switch float-end">
                        <input class="form-check-input" type="checkbox">
                    </div>
                </td>
            </tr>`;
}
