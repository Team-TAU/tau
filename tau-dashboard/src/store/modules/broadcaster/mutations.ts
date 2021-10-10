import { Broadcaster } from '@/models/broadcaster';
import { Mutations } from 'vuex-smart-module';
import BroadcasterState from './state';

export default class BroadcasterMutations extends Mutations<BroadcasterState> {
  loadRequest() {
    this.state.data = null;
    this.state.loading = true;
    this.state.error = '';
  }

  loadSuccess(payload: { broadcaster: Broadcaster }) {
    this.state.data = payload.broadcaster;
    this.state.loading = false;
    this.state.error = '';
  }
}
