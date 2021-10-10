import { Actions } from 'vuex-smart-module';
import TwitchEventsGetters from './getters';
import TwitchEventsMutations from './mutations';
import TwitchEventsState from './state';

import api$ from '@/services/tau-apis';
import { TwitchEvent } from '../../../models/twitch-event';

export default class TwitchEventsActions extends Actions<
  TwitchEventsState,
  TwitchEventsGetters,
  TwitchEventsMutations,
  TwitchEventsActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    return api$.tau.get('twitch-events', { active: true }).then(
      (resp) => {
        this.commit('loadAllSuccess', {
          twitchEvents: resp.results,
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
  createOne(payload: TwitchEvent) {
    this.commit('createOne', payload);
  }
  replay(payload: TwitchEvent) {
    return api$.tau.post(`twitch-events/${payload.id}/replay`, {}).then(
      (resp) => {
        return true;
      },
      (_err) => {
        return false;
      },
    );
  }
}
