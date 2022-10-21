import { Mutations } from 'vuex-smart-module';
import ChatBotChannelsState from './state';
import { ChatBotChannel } from '@/models/chat-bot';

export default class ChatBotChannelMutations extends Mutations<ChatBotChannelsState> {
  loadAllRequest() {
    this.state.entities = [];
    this.state.loading = true;
    this.state.error = '';
  }

  loadAllSuccess(payload: { chatBotChannels: ChatBotChannel[] }) {
    this.state.entities = payload.chatBotChannels;
    this.state.loading = false;
    this.state.error = '';
  }

  addOneSuccess(payload: { chatBotChannel: ChatBotChannel }) {
    this.state.entities = [...this.state.entities, payload.chatBotChannel];
  }

  deleteOneSuccess(payload: { chatBotChannel: ChatBotChannel }) {
    this.state.entities = this.state.entities.filter(
      (chatBot) => chatBot.id !== payload.chatBotChannel.id,
    );
  }

  deleteByIdSuccess(payload: { id: string }) {
    this.state.entities = this.state.entities.filter(
      (chatBot) => chatBot.id !== payload.id,
    );
  }
}
