import { Actions } from 'vuex-smart-module';
import UIState from './state';
import UIGetters from './getters';
import UIMutations from './mutations';
import { EventSubscription } from '@/models/event-subscription';

export default class UIActions extends Actions<
  UIState,
  UIGetters,
  UIMutations,
  UIActions
> {
  setTestFormView(payload: EventSubscription) {
    this.commit('setTestFormView', payload);
  }

  clearTestFormView() {
    this.commit('clearTestFormView');
  }
}
