import { TwitchHelixEndpoint } from '@/models/twitch-helix-endpoint';
import { Getters } from 'vuex-smart-module';
import TwitchHelixEndpointsState from './state';

export default class TwitchHelixEndpointsGetters extends Getters<TwitchHelixEndpointsState> {
  get all(): TwitchHelixEndpoint[] {
    return this.state.entities;
  }
}
