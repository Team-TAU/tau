import { Streamer } from '@/models/streamer';

export default class StreamersState {
  entities: Streamer[] = [];
  loading = false;
  error = '';
}
