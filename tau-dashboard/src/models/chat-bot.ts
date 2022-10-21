export interface ChatBot {
  id?: string;
  user_id: string;
  user_name: string;
  user_login: string;
  access_token?: string;
  refresh_token?: string;
  token_expiration?: string;
  connected?: boolean;
  created?: string;
  updated?: string;
}

export interface ChatBotChannel {
  id?: string;
  channel: string;
  chat_bot: string;
}

export interface ChatBotVM extends ChatBot {
  channels: ChatBotChannel[];
}
