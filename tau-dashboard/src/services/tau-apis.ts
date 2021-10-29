import { ajax } from 'rxjs/ajax';
import { map } from 'rxjs/operators';
import baseUrl from './base-api-url';

type QueryParams = Record<
  string,
  string | number | boolean | string[] | number[] | boolean[]
>;

class BaseApiService {
  basePath = '';

  constructor(basePath: string) {
    this.basePath = basePath;
  }

  get token() {
    const token = localStorage.getItem('tau-token');
    if (token === null) {
      throw new Error('No token currently exists.  You must authorize.');
    }
    return token;
  }

  get authHeader(): Readonly<Record<string, any>> {
    return {
      'Content-Type': 'application/json',
      Authorization: `Token ${this.token}`,
    };
  }

  get<T = any>(endpoint: string, queryParams: QueryParams = {}): Promise<T> {
    const queryStr =
      queryParams === {}
        ? ''
        : '?' +
          Object.keys(queryParams)
            .map((key) => `${key}=${queryParams[key]}`)
            .join('&');
    const url = `${baseUrl}${this.basePath}${endpoint}${queryStr}`;
    return ajax({
      url,
      method: 'GET',
      headers: this.authHeader,
    })
      .pipe(map((res) => res.response as T))
      .toPromise();
  }

  post<T = any>(endpoint: string, payload: any): Promise<T> {
    const url = `${baseUrl}${this.basePath}${endpoint}`;
    return ajax({
      url,
      method: 'POST',
      headers: this.authHeader,
      body: payload,
    })
      .pipe(map((res) => res.response as T))
      .toPromise();
  }

  put<T = any>(endpoint: string, payload: any): Promise<T> {
    const url = `${baseUrl}${this.basePath}${endpoint}`;
    return ajax({
      url,
      method: 'PUT',
      headers: this.authHeader,
      body: payload,
    })
      .pipe(map((res) => res.response as T))
      .toPromise();
  }

  patch<T = any>(endpoint: string, payload: any): Promise<T> {
    const url = `${baseUrl}${this.basePath}${endpoint}`;
    return ajax({
      url,
      method: 'PATCH',
      headers: this.authHeader,
      body: payload,
    })
      .pipe(map((res) => res.response as T))
      .toPromise();
  }

  delete(endpoint: string): Promise<void> {
    const url = `${baseUrl}${this.basePath}${endpoint}`;
    return ajax({
      url,
      method: 'DELETE',
      headers: this.authHeader,
    })
      .pipe(
        map((res) => {
          return;
        }),
      )
      .toPromise();
  }
}

class TauRestService extends BaseApiService {
  constructor() {
    super('/api/v1/');
  }
}

class TauHelixService extends BaseApiService {
  constructor() {
    super('/api/twitch/helix/');
  }
}

export default {
  tau: new TauRestService(),
  helix: new TauHelixService(),
};
