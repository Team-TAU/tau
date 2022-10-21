import { Store } from 'vuex';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { retryWhen, delay } from 'rxjs/operators';

import baseUrl from './base-api-url';

interface TwitchEventMessage {
  created: string;
  event_data: any;
  event_id: string;
  event_source: string;
  event_type: string;
  id: string;
  origin: string;
}

interface KeepAliveMessage {
  event: 'keep_alive';
}

abstract class BaseWsService {
  private ws: WebSocketSubject<unknown> | null = null;

  constructor(private endpoint: string) {
    console.log(`Constructed base WS Service for ${endpoint}`);
  }

  get baseWsUrl() {
    return baseUrl.replace('http', 'ws');
  }

  get token() {
    const token = localStorage.getItem('tau-token');
    if (token === null) {
      throw new Error('No token currently exists.  You must authorize.');
    }
    return token;
  }

  connect(): void {
    if (!this.ws) {
      this.connectJsonWs();
    }
  }

  disconnect(): void {
    this.ws?.complete();
    this.ws = null;
  }

  connectJsonWs(): void {
    try {
      // Create a webSocket subject, connecting to the ws widgets/json endpoint.
      this.ws = webSocket({
        url: `${this.baseWsUrl}/${this.endpoint}`,
        openObserver: {
          next: () => {
            console.log(`Connected to websocket at ${this.baseWsUrl}`);
            this.ws?.next({ token: this.token });
          },
        },
      });

      // Add a reconnect if connection dies using rxjs' subject pipe operator
      // then subscribe to any messages received by the subject.
      this.ws
        ?.pipe(
          // If we are disconnected, wait 2s before attempting to reconnect.
          retryWhen((err) => {
            console.log('Disconnected!  Attempting reconnection shortly...');
            return err.pipe(delay(2000));
          }),
        )
        .subscribe(
          // Once we receieve a message from the server, pass it to the handler function.
          (msg) => {
            this.handle(msg);
          },
        );
    } catch (err) {
      console.log(err);
    }
  }

  abstract handle(msg: any): void;
}

export class TauTwitchEventWsService extends BaseWsService {
  constructor(private store: Store<any>) {
    super('ws/twitch-events/');
  }

  handle(msg: TwitchEventMessage | KeepAliveMessage) {
    if ('event' in msg) {
      return;
    }
    this.store.dispatch('twitchEvents/createOne', msg);
    if (msg.event_type === 'stream-online') {
      this.store.dispatch(
        'streamers/streamerOnline',
        msg.event_data.broadcaster_user_id,
      );
    } else if (msg.event_type === 'stream-offline') {
      this.store.dispatch(
        'streamers/streamerOffline',
        msg.event_data.broadcaster_user_id,
      );
    }
  }
}

export class TauStatusWsService extends BaseWsService {
  constructor(private store: Store<any>) {
    super('ws/tau-status/');
  }

  handle(msg: any) {
    if ('event' in msg) {
      return;
    }
    this.store.dispatch('eventSubscriptions/updateOne', msg);
  }
}

export class ChatBotStatusWsService extends BaseWsService {
  constructor(private store: Store<any>) {
    super('ws/chat-bots/status/');
  }

  handle(msg: any) {
    if ('event' in msg) {
      return;
    }
    if (msg.event === 'Created') {
      this.store.dispatch('chatBots/addOne', msg.chatBot);
    } else {
      console.log('update not yet implemented');
    }
  }
}
