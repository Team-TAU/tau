import { Module } from 'vuex-smart-module';
import StreamerActions from './actions';
import StreamerGetters from './getters';
import StreamerMutations from './mutations';
import StreamersState from './state';

const streamers = new Module({
  state: StreamersState,
  getters: StreamerGetters,
  mutations: StreamerMutations,
  actions: StreamerActions,
});

export default streamers;
