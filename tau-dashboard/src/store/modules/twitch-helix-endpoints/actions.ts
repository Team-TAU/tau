import { Actions } from 'vuex-smart-module';
import TwitchHelixEndpointsGetters from './getters';
import TwitchHelixEndpointsMutations from './mutations';
import TwitchHelixEndpointsState from './state';

import api$ from '@/services/tau-apis';

export default class TwitchHelixEndpointsActions extends Actions<
  TwitchHelixEndpointsState,
  TwitchHelixEndpointsGetters,
  TwitchHelixEndpointsMutations,
  TwitchHelixEndpointsActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    return api$.tau.get('twitch/helix-endpoints').then(
      (resp) => {
        this.commit('loadAllSuccess', {
          twitchHelixEndpoints: resp,
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
}
