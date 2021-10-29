import { Module } from 'vuex-smart-module';
import AuthActions from './actions';
import AuthGetters from './getters';
import AuthMutations from './mutations';
import AuthState from './state';

const auth = new Module({
  state: AuthState,
  getters: AuthGetters,
  mutations: AuthMutations,
  actions: AuthActions,
});

export default auth;
