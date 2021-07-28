import { Mutations } from 'vuex-smart-module';
import { EventSubscription } from './models';
import EventSubState from './state';

export default class EventSubMutations extends Mutations<EventSubState> {
  loadAllRequest() {
    this.state.entities = [];
    this.state.loading = true;
    this.state.error = '';
  }

  loadAllSuccess(payload: { eventSubscriptions: EventSubscription[] }) {
    this.state.entities = payload.eventSubscriptions;
    this.state.loading = false;
    this.state.error = '';
  }
}
