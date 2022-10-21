import { Getters } from 'vuex-smart-module';
import ChatBotChannelsState from './state';
import { ChatBotChannel } from '@/models/chat-bot';

export default class ChatBotChannelGetters extends Getters<ChatBotChannelsState> {
  get all(): ChatBotChannel[] {
    return this.state.entities;
  }
}
