import { Module } from 'vuex-smart-module';
import UIState from './state';
import UIGetters from './getters';
import UIMutations from './mutations';
import UIActions from './actions';

const UI = new Module({
  state: UIState,
  getters: UIGetters,
  mutations: UIMutations,
  actions: UIActions,
});

export default UI;
