import { ChatBotChannel } from '@/models/chat-bot';

export default class ChatBotChannelsState {
  entities: ChatBotChannel[] = [];
  loading = false;
  error = '';
}
