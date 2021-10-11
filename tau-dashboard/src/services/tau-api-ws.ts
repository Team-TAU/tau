import { Store } from 'vuex';
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';
import { retryWhen, delay } from 'rxjs/operators';

import baseUrl from './base-api-url';

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

  handle(msg: any) {
    this.store.dispatch('twitchEvents/createOne', msg);
  }
}

export class TauStatusWsService extends BaseWsService {
  constructor(private store: Store<any>) {
    super('ws/tau-status/');
  }

  handle(msg: any) {
    this.store.dispatch('eventSubscriptions/updateOne', msg);
  }
}
