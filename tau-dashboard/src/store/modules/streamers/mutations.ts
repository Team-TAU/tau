import { Mutations } from 'vuex-smart-module';
import StreamersState from './state';
import { Streamer } from '@/models/streamer';

export default class StreamerMutations extends Mutations<StreamersState> {
  loadAllRequest() {
    this.state.entities = [];
    this.state.loading = true;
    this.state.error = '';
  }

  loadAllSuccess(payload: { streamers: Streamer[] }) {
    this.state.entities = payload.streamers;
    this.state.loading = false;
    this.state.error = '';
  }

  addOneSuccess(payload: { streamer: Streamer }) {
    this.state.entities = [...this.state.entities, payload.streamer];
  }

  deleteOneSuccess(payload: { streamer: Streamer }) {
    this.state.entities = this.state.entities.filter(
      (streamer) => streamer.id !== payload.streamer.id,
    );
  }
}
