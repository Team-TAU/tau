import { Mutations } from 'vuex-smart-module';
import AuthState from './state';

export default class AuthMutations extends Mutations<AuthState> {
  authSuccess(payload: { username: string; token: string }) {
    this.state.username = payload.username;
    this.state.token = payload.token;
    this.state.loggingIn = false;
    this.state.error = '';
  }

  authRequest() {
    this.state.username = '';
    this.state.token = '';
    this.state.loggingIn = true;
    this.state.error = '';
  }

  authError(payload: { error: string }) {
    this.state.username = '';
    this.state.token = '';
    this.state.loggingIn = false;
    this.state.error = payload.error;
  }

  authLogout() {
    this.state.username = '';
    this.state.token = '';
    this.state.loggingIn = false;
    this.state.error = '';
  }
}
