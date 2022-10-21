import { Actions } from 'vuex-smart-module';
import ChatBotChannelGetters from './getters';
import ChatBotChannelMutations from './mutations';
import ChatBotChannelsState from './state';
import { ChatBotChannel } from '@/models/chat-bot';

import api$ from '@/services/tau-apis';

export default class ChatBotChannelActions extends Actions<
  ChatBotChannelsState,
  ChatBotChannelGetters,
  ChatBotChannelMutations,
  ChatBotChannelActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    return api$.tau.get<ChatBotChannel[]>('chat-bots/channels').then(
      (resp) => {
        this.commit('loadAllSuccess', {
          chatBotChannels: resp,
        });
        return true;
      },
      (_err) => {
        // this.commit('authError', {
        //   error,
        // });
        return false;
      },
    );
  }

  addOne(payload: ChatBotChannel) {
    return api$.tau
      .post<ChatBotChannel>('chat-bots/channels', payload)
      .then((resp) => {
        this.commit('addOneSuccess', { chatBotChannel: resp });
      });
  }

  delete(payload: ChatBotChannel): Promise<boolean> {
    return api$.tau.delete(`chat-bots/channels/${payload.id}`).then(
      (resp) => {
        this.commit('deleteOneSuccess', {
          chatBotChannel: payload,
        });
        return true;
      },
      (_err) => {
        return false;
      },
    );
  }
}
