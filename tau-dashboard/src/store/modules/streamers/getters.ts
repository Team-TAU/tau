import { Getters } from 'vuex-smart-module';
import StreamersState from './state';
import { Streamer } from '@/models/streamer';

export default class StreamersGetters extends Getters<StreamersState> {
  get all(): Streamer[] {
    return this.state.entities;
  }

  get active(): Streamer[] {
    return this.state.entities.filter((streamer) => !streamer.disabled);
  }
}
