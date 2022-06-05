import { Module } from 'vuex-smart-module';
import ChatBotChannelActions from './actions';
import ChatBotChannelGetters from './getters';
import ChatBotChannelMutations from './mutations';
import ChatBotChannelsState from './state';

const chatBotChannels = new Module({
  state: ChatBotChannelsState,
  getters: ChatBotChannelGetters,
  mutations: ChatBotChannelMutations,
  actions: ChatBotChannelActions,
});

export default chatBotChannels;
