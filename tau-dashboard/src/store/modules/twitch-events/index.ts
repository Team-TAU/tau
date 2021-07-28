import { Module } from 'vuex-smart-module';
import TwitchEventsActions from './actions';
import TwitchEventsGetters from './getters';
import TwitchEventsMutations from './mutations';
import TwitchEventsState from './state';

const twitchEvents = new Module({
  state: TwitchEventsState,
  getters: TwitchEventsGetters,
  mutations: TwitchEventsMutations,
  actions: TwitchEventsActions,
});

export default twitchEvents;
