import { Module, createStore } from 'vuex-smart-module';
import auth from './modules/auth';
import eventSubscriptions from './modules/event-subscriptions';
import twitchEvents from './modules/twitch-events';

const root = new Module({
  modules: {
    auth,
    eventSubscriptions,
    twitchEvents,
  },
});

const store = createStore(root);

export default store;
