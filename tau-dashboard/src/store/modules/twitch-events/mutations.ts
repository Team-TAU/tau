import { Mutations } from 'vuex-smart-module';
import { TwitchEvent } from '../../../models/twitch-event';
import TwitchEventsState from './state';

export default class TwitchEventMutations extends Mutations<TwitchEventsState> {
  loadAllRequest() {
    this.state.entities = [];
    this.state.loading = true;
    this.state.error = '';
  }

  loadAllSuccess(payload: { twitchEvents: TwitchEvent[] }) {
    this.state.entities = payload.twitchEvents;
    this.state.loading = false;
    this.state.error = '';
  }

  createOne(payload: TwitchEvent) {
    this.state.entities = [payload, ...this.state.entities];
  }
}
