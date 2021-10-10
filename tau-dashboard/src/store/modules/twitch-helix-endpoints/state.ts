import { TwitchHelixEndpoint } from '@/models/twitch-helix-endpoint';

export default class TwitchHelixEndpointsState {
  entities: TwitchHelixEndpoint[] = [];
  loading = false;
  error = '';
  wsConnection = false;
}
