import { Module } from 'vuex-smart-module';
import TwitchOAuthScopesActions from './actions';
import TwitchOAuthScopesGetters from './getters';
import TwitchOAuthScopesMutations from './mutations';
import TwitchOAuthScopesState from './state';

const twitchOAuthScopes = new Module({
  state: TwitchOAuthScopesState,
  getters: TwitchOAuthScopesGetters,
  mutations: TwitchOAuthScopesMutations,
  actions: TwitchOAuthScopesActions,
});

export default twitchOAuthScopes;
