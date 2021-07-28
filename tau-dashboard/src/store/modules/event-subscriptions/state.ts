import { EventSubscription } from './models';

export default class EventSubscriptionsState {
  entities: EventSubscription[] = [];
  loading = false;
  error = '';
}
