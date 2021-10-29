import { Mutations } from 'vuex-smart-module';
import { EventSubscription } from '@/models/event-subscription';
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

  updateOne(payload: EventSubscription) {
    const idx = this.state.entities.findIndex(
      (eventSub) => eventSub.id === payload.id,
    );
    if (idx > -1) {
      this.state.entities = [
        ...this.state.entities.slice(0, idx),
        payload,
        ...this.state.entities.slice(idx + 1),
      ];
    }
  }
}
