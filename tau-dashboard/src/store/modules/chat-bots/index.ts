import { Module } from 'vuex-smart-module';
import ChatBotActions from './actions';
import ChatBotGetters from './getters';
import ChatBotMutations from './mutations';
import ChatBotsState from './state';

const chatBots = new Module({
  state: ChatBotsState,
  getters: ChatBotGetters,
  mutations: ChatBotMutations,
  actions: ChatBotActions,
});

export default chatBots;
