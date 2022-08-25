import json
import asyncio
import os

import requests
from pyngrok import ngrok
from pyngrok.exception import PyngrokError
import websockets

from django.conf import settings

from constance import config
from channels.db import database_sync_to_async

from tau.core.worker_irc import WorkerIrc
from tau.streamers.utils import update_all_streamers
from tau.chatbots.models import ChatBot
from .utils import (
    setup_ngrok,
    init_webhooks,
    refresh_access_token,
    teardown_all_acct_webhooks,
    teardown_webhooks,
    get_active_event_sub_ids,
)

class Worker:
    irc_url = 'wss://irc-ws.chat.twitch.tv'
    server_url = f'ws://localhost:{settings.BASE_PORT}/ws/worker-server/'
    connection = None
    server_connection = None
    loop = None
    tasks = []
    server_connected = False
    irc_connected = False
    public_url = ''
    wh_delay = 15
    irc_delay = 2
    active_event_sub_ids = []
    active_streamer_sub_ids = []
    ngrok_tunnel = None
    token_refreshed = False
    token = ''
    username = ''
    irc_bots = {}
    streamer_login = ''

    def __init__(self, token):
        self.tau_token = token
        config.TWITCH_APP_TOKEN_REFRESHED = False
        self.streamer_login = config.CHANNEL.lower()

    def setup_webhooks(self):
        twitch_access_token = config.TWITCH_APP_ACCESS_TOKEN
        if twitch_access_token != '':
            print('---- Establishing IRC and Webhook Connections ----')
            refresh_access_token()  # refresh the access token
            self.token_refreshed = True
            self.irc_bots[self.streamer_login].set_token_refreshed()
            # self.streamer_irc.set_token_refreshed()
            print('     [Access tokens refreshed]')
            if not config.RESET_ALL_WEBHOOKS:
                teardown_webhooks(self.tau_token)
                print('     [Old WebHooks torn down]')
            else:
                print('     [Tearing down all webhooks]')
                teardown_webhooks(self.tau_token)
                teardown_all_acct_webhooks()
                config.RESET_ALL_WEBHOOKS = False
            self.active_event_sub_ids, self.active_streamer_sub_ids = init_webhooks(
                self.public_url, self.tau_token)
            print('     [New WebHooks Initialized]')
            update_all_streamers()
            print('     [All streamer statuses updated]\n')
        else:
            print(
                'You have not yet set up a username, or authorized TAU to connect '
                'to your twitch account.  Webhooks will be set up after you do so.'
            )

    async def open_server_connection(self):
        delay = 1
        self.server_connection = await websockets.client.connect(self.server_url)
        if self.server_connection.open:
            print('    [WS CONNECTION BETWEEN WORKER AND SERVER UP]')
            self.server_connected = True
        else:
            self.server_connected = False
            print('---- Could not connect to server websocket.  Reconnecting... ----')
            await asyncio.sleep(delay)
            if delay < 120:
                delay = max(delay*2, 120)

    def create_event_loop(self):
        self.loop = asyncio.get_event_loop()
        self.tasks = [
            asyncio.ensure_future(self.manage_server_loop()),
            asyncio.ensure_future(self.manage_webhooks()),
            asyncio.ensure_future(self.manage_keep_alive()),
        ]
        for bot in self.irc_bots.values():
            self.tasks.append(asyncio.ensure_future(bot.manage_irc_loop()))
        self.loop.run_until_complete(asyncio.wait(self.tasks))

    async def manage_keep_alive(self):
        keep_alive_delay = os.environ.get("KEEP_ALIVE_DELAY", 120)
        while True:
            await asyncio.sleep(keep_alive_delay)
            await self.keep_alive()

    async def keep_alive(self):
        for _, bot in self.irc_bots.items():
            await bot.keep_alive()
        payload = {}
        headers = {
            'Authorization': f'Token {self.tau_token}',
            'Content-type': 'application/json'
        }
        for endpoint in [
            'twitch-events/keep-alive',
            'service-status/keep-alive',
            'chat-bots/status-keep-alive'
        ]:
            requests.post(
                f'{settings.LOCAL_URL}/api/v1/{endpoint}',
                json=payload,
                headers=headers
            )

    async def manage_server_loop(self):
        while True:
            if not self.server_connected:
                await self.connect_server()
            await asyncio.sleep(self.irc_delay)

    async def connect_server(self):
        await self.open_server_connection()
        await self.recieve_server()

    async def recieve_server(self):
        while True:
            try:
                message = json.loads(await self.server_connection.recv())
                action = message.get("action", "")
                if action == "irc-send":
                    await self.irc_send(message)
                elif action == "irc-subscribe":
                    await self.irc_subscribe(message)
                elif action == "irc-unsubscribe":
                    await self.irc_unsubscribe(message)
                elif action == "add-bot":
                    await self.add_bot(message.get("bot_id", ""))
                elif action == "add-bot-channel":
                    await self.add_bot_channel(message.get("bot", ""), message.get("channel", ""))
                elif action == "remove-bot-channel":
                    await self.remove_bot_channel(
                        message.get("bot", ""), message.get("channel", "")
                    )

            except websockets.exceptions.ConnectionClosed:
                print('Internal websocket to tau server unexpectedly closed... reconnecting')
                await self.open_server_connection()

    async def add_bot_channel(self, bot, channel):
        bot = self.irc_bots[bot]
        await bot.add_channel(channel)

    async def remove_bot_channel(self, bot, channel):
        bot = self.irc_bots[bot]
        await bot.remove_channel(channel)

    async def add_bot(self, bot_id):
        await asyncio.sleep(1)
        bot = await database_sync_to_async(self.get_bot)(bot_id)
        self.irc_bots[bot.user_login] = await database_sync_to_async(self.create_irc_worker)(bot)
        event_loop = self.loop
        asyncio.ensure_future(self.irc_bots[bot.user_login].manage_irc_loop(), loop=event_loop)

    async def irc_subscribe(self, message):
        bot_username = message.get("irc_username")
        self.irc_bots[bot_username].subscribe()

    async def irc_unsubscribe(self, message):
        bot_username = message.get("irc_username")
        await self.irc_bots[bot_username].unsubscribe()

    async def irc_send(self, message):
        bot_username = message.get("irc_username", "")
        irc_channel = message.get("irc_channel", "")
        message = message.get("message", "")
        await self.irc_bots[bot_username].send(
            channel=irc_channel, message=message
        )

    async def send_server(self, message):
        await self.server_connection.send(message)

    async def manage_webhooks(self):
        refresh_webhooks = True
        while True:
            refreshed_ngrok = False
            if settings.USE_NGROK and self.ngrok_tunnel is None:
                self.public_url, self.ngrok_tunnel = await database_sync_to_async(setup_ngrok)()
                refreshed_ngrok = True
            elif settings.USE_NGROK:
                # Check to see if tunnel is still alive
                r = requests.get(f'{self.public_url}/api/v1/heartbeat')
                if r.status_code != 200:
                    try:
                        ngrok.disconnect(self.ngrok_tunnel.public_url)
                    except PyngrokError:
                        pass

                    self.public_url, self.ngrok_tunnel = await database_sync_to_async(setup_ngrok)()
                    refreshed_ngrok = True
            else:
                self.public_url = settings.BASE_URL
                await database_sync_to_async(self.set_setting)('PUBLIC_URL', settings.BASE_URL)
            # check for difference in required webhooks:
            new_event_sub_ids = await database_sync_to_async(get_active_event_sub_ids)()
            scopes_refreshed = await database_sync_to_async(self.lookup_setting)('SCOPES_REFRESHED')
            if set(self.active_event_sub_ids) != set(new_event_sub_ids) and scopes_refreshed:
                refresh_webhooks = True
                await database_sync_to_async(self.set_setting)('SCOPES_REFRESHED', False)

            if refresh_webhooks or refreshed_ngrok:
                await database_sync_to_async(self.setup_webhooks)()
                refresh_webhooks = False

            force_refresh_webhooks = await database_sync_to_async(
                self.lookup_setting
            )('FORCE_WEBHOOK_REFRESH')

            if force_refresh_webhooks:
                await database_sync_to_async(self.setup_webhooks)()
                await database_sync_to_async(self.set_setting)('FORCE_WEBHOOK_REFRESH', False)

            await asyncio.sleep(self.wh_delay)

    def run(self):
        self.token = config.TWITCH_ACCESS_TOKEN
        self.username = config.CHANNEL

        # self.streamer_irc = WorkerIrc(tau_token=self.tau_token, streamer=self.username)
        self.irc_bots = {bot.user_login: WorkerIrc(tau_token=self.tau_token, bot=bot)
                         for bot in ChatBot.objects.all()}
        self.irc_bots[self.username.lower()] = WorkerIrc(
            tau_token=self.tau_token, streamer=self.username
        )

        self.create_event_loop()

    async def check_irc_settings(self):
        while True:
            await asyncio.sleep(self.irc_delay)
            use_irc = await database_sync_to_async(self.lookup_setting)('USE_IRC')
            if not use_irc and self.irc_connected:
                await self.connection.close()
                self.irc_connected = False
                print('---- Disconnected from twitch irc ws server ----')

    def lookup_setting(self, setting):
        return getattr(config, setting)

    def set_setting(self, setting, value):
        setattr(config, setting, value)

    def get_bot(self, bot_id):
        bot = ChatBot.objects.get(pk=bot_id)
        print(f'Got bot: {bot}')
        return bot

    def create_irc_worker(self, bot):
        irc_worker = WorkerIrc(tau_token=self.tau_token, bot=bot)
        return irc_worker
