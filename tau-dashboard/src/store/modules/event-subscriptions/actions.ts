import { ajax } from 'rxjs/ajax';
import { map } from 'rxjs/operators';
import { Actions } from 'vuex-smart-module';
import EventSubGetters from './getters';
import EventSubMutations from './mutations';
import EventSubState from './state';

export default class EventSubActions extends Actions<
  EventSubState,
  EventSubGetters,
  EventSubMutations,
  EventSubActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    const baseUrl =
      process.env.NODE_ENV === 'development'
        ? `http://localhost:${process.env.VUE_APP_API_PORT}`
        : '';
    const url = `${baseUrl}/api/v1/twitch/eventsub-subscriptions?active=true`;
    const token = localStorage.getItem('tau-token');
    const headers = {
      Authorization: `Token ${token}`,
    };
    return ajax({
      url,
      method: 'GET',
      headers,
    })
      .pipe(map((resp) => resp.response))
      .toPromise()
      .then(
        (resp) => {
          this.commit('loadAllSuccess', {
            eventSubscriptions: resp,
          });
          return true;
        },
        (err) => {
          // this.commit('authError', {
          //   error,
          // });
          return false;
        },
      );
  }
}
