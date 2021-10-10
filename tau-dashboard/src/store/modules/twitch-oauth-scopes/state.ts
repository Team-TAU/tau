import { TwitchOAuthScope } from '@/models/twitch-oauth-scope';

export default class TwitchOAuthScopesState {
  entities: TwitchOAuthScope[] = [];
  loading = false;
  error = '';
  wsConnection = false;
}
