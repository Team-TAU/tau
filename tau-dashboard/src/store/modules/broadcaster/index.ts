import { Module } from 'vuex-smart-module';
import BroadcasterActions from './actions';
import BroadcasterGetters from './getters';
import BroadcasterMutations from './mutations';
import BroadcasterState from './state';

const broadcaster = new Module({
  state: BroadcasterState,
  getters: BroadcasterGetters,
  mutations: BroadcasterMutations,
  actions: BroadcasterActions,
});

export default broadcaster;
