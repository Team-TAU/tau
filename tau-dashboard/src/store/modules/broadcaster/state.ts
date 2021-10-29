import { Broadcaster } from '@/models/broadcaster';

export default class BroadcasterState {
  data: Broadcaster | null = null;
  loading = false;
  error = '';
}
