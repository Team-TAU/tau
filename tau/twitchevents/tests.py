from django.test import TestCase
from .ircclient import IrcClient


def test_irc_client_parse_message_on_normal_msg():
    irc = IrcClient()
    raw_msg = '@badge-info=subscriber/32;badges=broadcaster/1,subscriber/3012,premium/1;client-nonce=83a18f05ee1a98055fa84924b4de2817;color=#FFFFFF;display-name=wwsean08;emotes=;flags=;id=f3397bdf-cc9e-49c1-ad2e-d00a1a3db852;mod=0;room-id=47073625;subscriber=1;tmi-sent-ts=1625117410997;turbo=0;user-id=47073625;user-type= :wwsean08!wwsean08@wwsean08.tmi.twitch.tv PRIVMSG #wwsean08 :test\r\n'
    msg = irc.parse_message(raw_msg)

    assert msg['raw'] == raw_msg
    assert len(msg["tags"]) == 15
    assert msg['tags']['display-name'] == 'wwsean08'
    assert len(msg['params']) == 3
    assert msg['params'][0] == 'PRIVMSG'
    assert msg['params'][1] == '#wwsean08'
    assert 'test' in msg['params'][2]


def test_irc_client_parse_message_on_channel_points_redemption():
    irc = IrcClient()
    raw_msg = '@badge-info=subscriber/32;badges=broadcaster/1,subscriber/3012,premium/1;color=#FFFFFF;display-name=wwsean08;emotes=;flags=;id=d819b667-0b5c-4777-aabe-86ceeb54da4d;mod=0;msg-id=highlighted-message;room-id=47073625;subscriber=1;tmi-sent-ts=1625118022522;turbo=0;user-id=47073625;user-type= :wwsean08!wwsean08@wwsean08.tmi.twitch.tv PRIVMSG #wwsean08 :highlight\r\n'
    msg = irc.parse_message(raw_msg)

    assert msg['raw'] == raw_msg
    assert len(msg['params']) == 3
    assert len(msg['tags']) == 15
    assert 'emotes' in msg['tags']
    assert msg['tags']['emotes'] == ''

    raw_msg = '@badge-info=subscriber/32;badges=broadcaster/1,subscriber/3012,premium/1;color=#FFFFFF;display-name=wwsean08;emote-only=1;emotes=25:0-4;flags=;id=723eb0ab-c799-40f4-9d3f-d5d95e78a859;mod=0;msg-id=highlighted-message;room-id=47073625;subscriber=1;tmi-sent-ts=1625118271555;turbo=0;user-id=47073625;user-type= :wwsean08!wwsean08@wwsean08.tmi.twitch.tv PRIVMSG #wwsean08 :Kappa\r\n'
    msg = irc.parse_message(raw_msg)

    assert msg['raw'] == raw_msg
    assert len(msg['params']) == 3
    assert 'Kappa' in msg['params'][2]
    assert len(msg['tags']) == 16
    assert 'emotes' in msg['tags']
    assert msg['tags']['emotes'] == '25:0-4'
    assert msg['tags']['msg-id'] == 'highlighted-message'
    assert msg['tags']['emote-only'] == '1'

    raw_msg = '@badge-info=subscriber/32;badges=broadcaster/1,subscriber/3012,premium/1;color=#FFFFFF;display-name=wwsean08;emotes=25:0-4;flags=;id=0aa1e93c-7bab-41fd-97c9-9d013e2da080;mod=0;msg-id=highlighted-message;room-id=47073625;subscriber=1;tmi-sent-ts=1625119203507;turbo=0;user-id=47073625;user-type= :wwsean08!wwsean08@wwsean08.tmi.twitch.tv PRIVMSG #wwsean08 :Kappa with message\r\n'
    msg = irc.parse_message(raw_msg)

    assert msg['raw'] == raw_msg
    assert len(msg['params']) == 3
    assert 'Kappa' in msg['params'][2]
    assert len(msg['tags']) == 15
    assert 'emotes' in msg['tags']
    assert msg['tags']['emotes'] == '25:0-4'
    assert msg['tags']['msg-id'] == 'highlighted-message'
    assert 'emote-only' not in msg['tags']

    raw_msg = '@badge-info=subscriber/32;badges=broadcaster/1,subscriber/3012,premium/1;color=#FFFFFF;custom-reward-id=f18636db-ed73-4d2b-a091-bdbd5fff45e5;display-name=wwsean08;emotes=;flags=;id=e58e178f-9332-4271-8b56-b44f12afb29f;mod=0;room-id=47073625;subscriber=1;tmi-sent-ts=1625118870432;turbo=0;user-id=47073625;user-type= :wwsean08!wwsean08@wwsean08.tmi.twitch.tv PRIVMSG #wwsean08 :#ff0000\r\n'
    msg = irc.parse_message(raw_msg)

    assert msg['raw'] == raw_msg
    assert len(msg['params']) == 3
    assert '#ff0000' in msg['params'][2]
    assert len(msg['tags']) == 15
    assert 'custom-reward-id' in msg['tags']
    assert msg['tags']['custom-reward-id'] == 'f18636db-ed73-4d2b-a091-bdbd5fff45e5'


def test_irc_client_parse_message_on_join():
    irc = IrcClient()
    raw_msg = ':streamlabs!streamlabs@streamlabs.tmi.twitch.tv JOIN #wwsean08\r\n'
    msg = irc.parse_message(raw_msg)

    assert msg['raw'] == raw_msg
    assert msg['command'] == 'JOIN'
    assert msg['tags'] == {}
    assert len(msg['params']) == 2
    assert msg['params'][0] == 'JOIN'
    assert '#wwsean08' in msg['params'][1]


def test_irc_client_parse_message_on_ping():
    irc = IrcClient()
    raw_msg = 'PING :tmi.twitch.tv\r\n'
    msg = irc.parse_message(raw_msg)

    assert msg['raw'] == raw_msg
    assert msg['prefix'] is None
    assert msg['params'][0] == "PING"
    assert "tmi.twitch.tv" in msg['params'][1]