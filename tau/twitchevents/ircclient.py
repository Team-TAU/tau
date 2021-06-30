import pprint

import websockets
import asyncio

from constance import config

class IrcClient():
    url = 'wss://irc-ws.chat.twitch.tv'
    connection = None

    async def connect(self):
        delay = 1
        while True:
            self.connection = await websockets.client.connect(self.url)
            if self.connection.open:
                print('---- Connected to twitch irc ws server ----')
                await self.initial_connect()
                break
            else:
                print(f'---- Could not connect, waiting {delay}s to reconnect ----')
                await asyncio.sleep(delay)
                if delay < 120:
                    delay = max(delay*2, 120)

    def run(self):
        self.token = config.TWITCH_ACCESS_TOKEN
        self.username = config.CHANNEL
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.connect())
        tasks = [
            asyncio.ensure_future(self.recieve()),
        ]
        loop.run_until_complete(asyncio.wait(tasks))

    async def initial_connect(self):
        caps = 'twitch.tv/tags twitch.tv/commands twitch.tv/membership'
        await self.connection.send(f'CAP REQ :{caps}')
        await self.connection.send(f'PASS oauth:{self.token}')
        await self.connection.send(f'NICK {self.username}')
        await self.connection.send(f'JOIN #{self.username.lower()}')

    async def recieve(self):
        print('Recieve!!')
        pp = pprint.PrettyPrinter(indent=2)
        while True:
            try:
                message = await self.connection.recv()
                data = self.parse_message(message)
                pp.pprint(data)
            except websockets.exceptions.ConnectionClosed:
                print('Websocket to twitch closed... reconnecting')
                await self.connect()

    def parse_message(self, data):
        message = {
            'raw': data,
            'tags': {},
            'prefix': None,
            'command': None,
            'params': []
        }

        position = 0
        nextspace = 0

        if data[0] == '@':
            nextspace = data.find(' ')
            if(nextspace == -1):
                return None

            rawTags = data[1:nextspace].split(';')
            for tag in rawTags:
                pair = tag.split('=')
                if len(pair) == 1:
                    value = True
                else:
                    value = pair[1]
                message['tags'][pair[0]] = value
            position = nextspace + 1

            while data[position] == ' ':
                position += 1
            
        if data[position] == ':':
            nextspace = data.find(' ', position)

            if nextspace == -1:
                return None
            
            message['prefix'] = data[position:nextspace]

            position = nextspace + 1

            while data[position] == ' ':
                position += 1

        nextspace = data.find(' ', position)

        if nextspace == -1:
            if len(data) > position:
                message['command'] = data[position:]
            else:
                message['command'] = None
            return message
        
        message['command'] = data[position:nextspace]

        while data[position] == ' ':
            position+=1
        
        while position < len(data):
            nextspace = data.find(' ', position)
            if data[position] == ':':
                message['params'].append(data[position:])
                break

            if nextspace != -1:
                message['params'].append(data[position:nextspace])
                position = nextspace + 1

                while data[position] == ' ':
                    position += 1
                
                continue
        
            if nextspace == -1:
                message['params'].append(data[position:])
                break
            
        return message



