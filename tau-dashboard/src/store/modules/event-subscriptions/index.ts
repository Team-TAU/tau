import { Module } from 'vuex-smart-module';
import EventSubActions from './actions';
import EventSubGetters from './getters';
import EventSubMutations from './mutations';
import EventSubState from './state';

const eventSub = new Module({
  state: EventSubState,
  getters: EventSubGetters,
  mutations: EventSubMutations,
  actions: EventSubActions,
});

export default eventSub;
