import { Actions } from 'vuex-smart-module';
import TwitchOAuthScopeGetters from './getters';
import TwitchOAuthScopeMutations from './mutations';
import TwitchOAuthScopesState from './state';

import api$ from '@/services/tau-apis';
import { TwitchOAuthScope } from '@/models/twitch-oauth-scope';

export default class TwitchOAuthScopesActions extends Actions<
  TwitchOAuthScopesState,
  TwitchOAuthScopeGetters,
  TwitchOAuthScopeMutations,
  TwitchOAuthScopesActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    return api$.tau.get('twitch/scopes').then(
      (resp) => {
        this.commit('loadAllSuccess', {
          twitchOAuthScopes: resp,
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
  bulkUpdate(payload: TwitchOAuthScope[]) {
    return api$.tau.put('twitch/scopes/bulk', payload).then(
      (resp) => {
        this.commit('loadAllSuccess', {
          twitchOAuthScopes: resp,
        });
        return true;
      },
      (_err) => {
        return false;
      },
    );
  }
}
