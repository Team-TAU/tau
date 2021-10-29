import { EventSubscription } from '@/models/event-subscription';
import { Mutations } from 'vuex-smart-module';
import UIState from './state';

export default class UIMutations extends Mutations<UIState> {
  setTestFormView(payload: EventSubscription) {
    this.state.testFormView = payload;
  }

  clearTestFormView() {
    this.state.testFormView = null;
  }
}
