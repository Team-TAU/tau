import { ajax } from 'rxjs/ajax';
import { map } from 'rxjs/operators';

import Cookies from 'js-cookie';

import { Actions } from 'vuex-smart-module';
import AuthGetters from './getters';
import AuthMutations from './mutations';
import AuthState from './state';

export default class AuthActions extends Actions<
  AuthState,
  AuthGetters,
  AuthMutations,
  AuthActions
> {
  login(payload: { username: string; password: string }): Promise<boolean> {
    this.commit('authRequest');
    const baseUrl =
      process.env.NODE_ENV === 'development'
        ? `http://localhost:${process.env.VUE_APP_API_PORT}`
        : window.location.origin;
    const csrftoken = Cookies.get('csrftoken');
    const url = `${baseUrl}/api-token-auth/`;
    const headers = csrftoken ? { 'X-CSRFToken': csrftoken } : {};
    return ajax({
      url,
      method: 'POST',
      body: payload,
      headers,
    })
      .pipe(map((resp) => resp.response))
      .toPromise()
      .then(
        (resp) => {
          localStorage.setItem('tau-username', payload.username);
          localStorage.setItem('tau-token', resp.token);
          this.commit('authSuccess', {
            username: payload.username,
            token: resp.token,
          });
          return true;
        },
        (err) => {
          const error =
            err.status === 400
              ? 'Incorrect username or password.'
              : 'An error occurred.  Please try again.';
          this.commit('authError', {
            error,
          });
          return false;
        },
      );
  }

  logout(): Promise<void> {
    return new Promise<void>((resolve) => {
      this.commit('authLogout');
      localStorage.removeItem('tau-username');
      localStorage.removeItem('tau-token');
      resolve();
    });
  }
}
