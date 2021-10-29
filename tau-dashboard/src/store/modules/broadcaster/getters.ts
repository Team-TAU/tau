import { Broadcaster } from '@/models/broadcaster';
import { Getters } from 'vuex-smart-module';
import BroadcasterState from './state';

export default class BroadcasterGetters extends Getters<BroadcasterState> {
  get data(): Broadcaster | null {
    return this.state.data;
  }
}
