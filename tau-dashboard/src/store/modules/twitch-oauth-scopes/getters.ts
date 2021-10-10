import { TwitchOAuthScope } from '@/models/twitch-oauth-scope';
import { Getters } from 'vuex-smart-module';
import TwitchOAuthScopesState from './state';

export default class TwitchOAuthScopeGetters extends Getters<TwitchOAuthScopesState> {
  get all(): TwitchOAuthScope[] {
    return this.state.entities;
  }
}
