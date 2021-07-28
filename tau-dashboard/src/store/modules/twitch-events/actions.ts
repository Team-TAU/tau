import { ajax } from 'rxjs/ajax';
import { map } from 'rxjs/operators';
import { Actions } from 'vuex-smart-module';
import TwitchEventsGetters from './getters';
import TwitchEventsMutations from './mutations';
import TwitchEventsState from './state';

export default class TwitchEventsActions extends Actions<
  TwitchEventsState,
  TwitchEventsGetters,
  TwitchEventsMutations,
  TwitchEventsActions
> {
  loadAll(): Promise<boolean> {
    this.commit('loadAllRequest');
    const baseUrl =
      process.env.NODE_ENV === 'development'
        ? `http://localhost:${process.env.VUE_APP_API_PORT}`
        : '';
    const url = `${baseUrl}/api/v1/twitch-events`;
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
            twitchEvents: resp.results,
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
