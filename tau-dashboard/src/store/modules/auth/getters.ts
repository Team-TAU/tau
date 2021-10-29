import { Getters } from 'vuex-smart-module';
import AuthState from './state';

export default class AuthGetters extends Getters<AuthState> {
  get username(): string {
    return this.state.username;
  }

  get token(): string {
    return this.state.token;
  }

  get loggingIn(): boolean {
    return this.state.loggingIn;
  }

  get isAuthenticated(): boolean {
    return !!this.state.token;
  }

  get error(): string {
    return this.state.error;
  }
}
