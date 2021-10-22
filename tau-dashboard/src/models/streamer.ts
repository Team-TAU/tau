export interface Streamer {
  id?: string;
  twitch_id?: string;
  twitch_username: string;
  disabled: boolean;
  streaming: boolean;
  created?: string;
  updated?: string;
}
