import { Getters } from 'vuex-smart-module';
import { EventSubscription } from './models';
import EventSubState from './state';

export default class EventSubGetters extends Getters<EventSubState> {
  get all(): EventSubscription[] {
    return this.state.entities;
  }

  get entities(): { [key: string]: EventSubscription } {
    const emptyAcc: { [key: string]: EventSubscription } = {};
    return this.state.entities.reduce((acc, val) => {
      acc[val.id] = val;
      return acc;
    }, emptyAcc);
  }
}
