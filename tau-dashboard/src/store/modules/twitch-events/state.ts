import { TwitchEvent } from '@/models/twitch-event';

export default class TwitchEventsState {
  entities: TwitchEvent[] = [];
  loading = false;
  error = '';
  wsConnection = false;
}
