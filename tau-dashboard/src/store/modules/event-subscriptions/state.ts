import { EventSubscription } from '@/models/event-subscription';

export default class EventSubscriptionsState {
  entities: EventSubscription[] = [];
  loading = false;
  error = '';
  wsConnection = false;
}
