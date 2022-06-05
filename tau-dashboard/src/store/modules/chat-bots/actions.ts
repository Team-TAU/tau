import { Actions } from 'vuex-smart-module';
import ChatBotGetters from './getters';
import ChatBotMutations from './mutations';
import ChatBotsState from './state';
import { ChatBot } from '@/models/chat-bot';

import api$ from '@/services/tau-apis';

interface ChatBotListResponse {
  next: string;
  previous: string;
  results: ChatBot[];
}

export default class ChatBotActions extends Actions<
  ChatBotsState,
  ChatBotGetters,
  ChatBotMutations,
  ChatBotActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    return api$.tau.get<ChatBotListResponse>('chat-bots').then(
      (resp) => {
        this.commit('loadAllSuccess', {
          chatBots: resp.results,
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

  addOne(payload: ChatBot) {
    this.commit('addOneSuccess', { chatBot: payload });
  }

  delete(payload: ChatBot): Promise<boolean> {
    return api$.tau.delete(`chat-bots/${payload.id}`).then(
      (resp) => {
        this.commit('deleteOneSuccess', {
          chatBot: payload,
        });
        return true;
      },
      (_err) => {
        return false;
      },
    );
  }
}
