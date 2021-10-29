import { Module } from 'vuex-smart-module';
import TwitchHelixEndpointsActions from './actions';
import TwitchHelixEndpointsGetters from './getters';
import TwitchHelixEndpointsMutations from './mutations';
import TwitchHelixEndpointsState from './state';

const twitchHelixEndpoints = new Module({
  state: TwitchHelixEndpointsState,
  getters: TwitchHelixEndpointsGetters,
  mutations: TwitchHelixEndpointsMutations,
  actions: TwitchHelixEndpointsActions,
});

export default twitchHelixEndpoints;
