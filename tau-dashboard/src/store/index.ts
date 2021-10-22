import { Module, createStore } from 'vuex-smart-module';
import auth from './modules/auth';
import broadcaster from './modules/broadcaster';
import eventSubscriptions from './modules/event-subscriptions';
import twitchEvents from './modules/twitch-events';
import twitchHelixEndpoints from './modules/twitch-helix-endpoints';
import twitchOAuthScopes from './modules/twitch-oauth-scopes';
import streamers from './modules/streamers';
import UI from './modules/ui';

const root = new Module({
  modules: {
    auth,
    broadcaster,
    eventSubscriptions,
    streamers,
    twitchEvents,
    twitchHelixEndpoints,
    twitchOAuthScopes,
    UI,
  },
});

const store = createStore(root);

export default store;
