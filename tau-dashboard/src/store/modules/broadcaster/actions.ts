import api$ from '@/services/tau-apis';
import { Actions } from 'vuex-smart-module';
import BroadcasterGetters from './getters';
import BroadcasterMutations from './mutations';
import BroadcasterState from './state';

export default class BroadcasterActions extends Actions<
  BroadcasterState,
  BroadcasterGetters,
  BroadcasterMutations,
  BroadcasterActions
> {
  load(): Promise<boolean> {
    this.commit('loadRequest');
    return api$.helix.get('users').then(
      (resp) => {
        this.commit('loadSuccess', {
          broadcaster: resp.data[0],
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
