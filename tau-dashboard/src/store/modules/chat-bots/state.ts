import { ChatBot } from '@/models/chat-bot';

export default class ChatBotsState {
  entities: ChatBot[] = [];
  loading = false;
  error = '';
}
