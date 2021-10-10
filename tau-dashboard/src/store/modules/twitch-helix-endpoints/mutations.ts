import { TwitchHelixEndpoint } from '@/models/twitch-helix-endpoint';
import { Mutations } from 'vuex-smart-module';
import TwitchHelixEndpointsState from './state';

export default class TwitchHelixEndpointsMutations extends Mutations<TwitchHelixEndpointsState> {
  loadAllRequest() {
    this.state.entities = [];
    this.state.loading = true;
    this.state.error = '';
  }

  loadAllSuccess(payload: { twitchHelixEndpoints: TwitchHelixEndpoint[] }) {
    this.state.entities = payload.twitchHelixEndpoints;
    this.state.loading = false;
    this.state.error = '';
  }
}
