import { Getters } from 'vuex-smart-module';
import ChatBotsState from './state';
import { ChatBot } from '@/models/chat-bot';

export default class ChatBotGetters extends Getters<ChatBotsState> {
  get all(): ChatBot[] {
    return this.state.entities;
  }
}
