import { TwitchOAuthScope } from '@/models/twitch-oauth-scope';
import { Mutations } from 'vuex-smart-module';
import TwitchOAuthScopesState from './state';

export default class TwitchOAuthScopesMutations extends Mutations<TwitchOAuthScopesState> {
  loadAllRequest() {
    this.state.entities = [];
    this.state.loading = true;
    this.state.error = '';
  }

  loadAllSuccess(payload: { twitchOAuthScopes: TwitchOAuthScope[] }) {
    this.state.entities = payload.twitchOAuthScopes;
    this.state.loading = false;
    this.state.error = '';
  }
}
