import { TwitchEvent } from './models';

export default class TwitchEventsState {
  entities: TwitchEvent[] = [];
  loading = false;
  error = '';
}
