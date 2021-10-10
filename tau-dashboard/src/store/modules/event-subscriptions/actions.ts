import { Actions } from 'vuex-smart-module';
import EventSubGetters from './getters';
import EventSubMutations from './mutations';
import EventSubState from './state';

import api$ from '@/services/tau-apis';
import { EventSubscription } from '@/models/event-subscription';

export default class EventSubActions extends Actions<
  EventSubState,
  EventSubGetters,
  EventSubMutations,
  EventSubActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    return api$.tau.get('twitch/eventsub-subscriptions').then(
      (resp) => {
        this.commit('loadAllSuccess', {
          eventSubscriptions: resp,
        });
        return true;
      },
      (_err) => {
        // this.commit('authError', {
        //   error,
        // });
        return false;
      },
    );
  }

  updateOne(payload: EventSubscription) {
    this.commit('updateOne', payload);
  }

  bulkActivate(payload: { id: string; active: boolean }[]) {
    return api$.tau
      .put('twitch/eventsub-subscriptions/bulk-activate', payload)
      .then(
        (resp) => {
          this.commit('loadAllSuccess', {
            eventSubscriptions: resp,
          });
          return true;
        },
        (_err) => {
          return false;
        },
      );
  }
}
