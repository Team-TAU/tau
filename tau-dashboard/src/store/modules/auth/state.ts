// State
export default class AuthState {
  username = localStorage.getItem('tau-username') || '';
  token = localStorage.getItem('tau-token') || '';
  loggingIn = false;
  error = '';
}
