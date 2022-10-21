import { Mutations } from 'vuex-smart-module';
import ChatBotsState from './state';
import { ChatBot } from '@/models/chat-bot';

export default class ChatBotMutations extends Mutations<ChatBotsState> {
  loadAllRequest() {
    this.state.entities = [];
    this.state.loading = true;
    this.state.error = '';
  }

  loadAllSuccess(payload: { chatBots: ChatBot[] }) {
    this.state.entities = payload.chatBots;
    this.state.loading = false;
    this.state.error = '';
  }

  addOneSuccess(payload: { chatBot: ChatBot }) {
    this.state.entities = [...this.state.entities, payload.chatBot];
  }

  deleteOneSuccess(payload: { chatBot: ChatBot }) {
    this.state.entities = this.state.entities.filter(
      (chatBot) => chatBot.id !== payload.chatBot.id,
    );
  }
}
