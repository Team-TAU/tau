import { Getters } from 'vuex-smart-module';
import { TwitchEvent } from '../../../models/twitch-event';
import TwitchEventsState from './state';

export default class EventSubGetters extends Getters<TwitchEventsState> {
  get all(): TwitchEvent[] {
    return this.state.entities;
  }

  get entities(): { [key: string]: TwitchEvent } {
    const emptyAcc: { [key: string]: TwitchEvent } = {};
    return this.state.entities.reduce((acc, val) => {
      acc[val.id] = val;
      return acc;
    }, emptyAcc);
  }
}
