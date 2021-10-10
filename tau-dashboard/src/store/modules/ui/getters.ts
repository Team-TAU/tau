import { EventSubscription } from '@/models/event-subscription';
import { Getters } from 'vuex-smart-module';
import UIState from './state';

export default class UIGetters extends Getters<UIState> {
  get testFormView(): EventSubscription | null {
    return this.state.testFormView;
  }
}
