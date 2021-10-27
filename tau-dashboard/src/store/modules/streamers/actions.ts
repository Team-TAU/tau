import { Actions } from 'vuex-smart-module';
import StreamerGetters from './getters';
import StreamerMutations from './mutations';
import StreamersState from './state';

import api$ from '@/services/tau-apis';
import { Streamer } from '@/models/streamer';

interface StreamerListResponse {
  next: string;
  previous: string;
  results: Streamer[];
}

export default class StreamerActions extends Actions<
  StreamersState,
  StreamerGetters,
  StreamerMutations,
  StreamerActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    return api$.tau.get<StreamerListResponse>('streamers').then(
      (resp) => {
        this.commit('loadAllSuccess', {
          streamers: resp.results,
        });
        return true;
      },
      (_err) => {
        // this.commit('authError', {
        //   error,
        // });
        return false;
      },
    );
  }

  create(payload: Streamer): Promise<boolean> {
    return api$.tau.post<Streamer>('streamers', payload).then(
      (resp) => {
        this.commit('addOneSuccess', {
          streamer: resp,
        });
        return true;
      },
      (_err) => {
        return false;
      },
    );
  }

  delete(payload: Streamer): Promise<boolean> {
    return api$.tau.delete(`streamers/${payload.id}`).then(
      (resp) => {
        this.commit('deleteOneSuccess', {
          streamer: payload,
        });
        return true;
      },
      (_err) => {
        return false;
      },
    );
  }

  streamerOnline(payload: string) {
    this.commit('streamerStatus', { id: payload, streaming: true });
  }

  streamerOffline(payload: string) {
    this.commit('streamerStatus', { id: payload, streaming: false });
  }
}
