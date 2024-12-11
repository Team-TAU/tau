import { defineStore } from "pinia";

interface State {
    username: string;
    token: string;
    loggingIn: boolean;
    error: string;
}

export const useAuthStore = defineStore('auth', {
    state: (): State => ({
        username: localStorage.getItem('tau-username') || '',
        token: localStorage.getItem('tau-token') || '',
        loggingIn: false,
        error: '',
    }),
    getters: {
        isAuthenticated: (state) => !!state.token,
    },
    actions: {
        logout() {
            localStorage.removeItem("tau-username");
            localStorage.removeItem("tau-token");
            this.username = '';
            this.token = '';
            this.loggingIn = false;
            this.error = '';
        },
        authSuccess(payload: { username: string; token: string }) {
            this.username = payload.username;
            this.token = payload.token;
            localStorage.setItem("tau-username", payload.username);
            localStorage.setItem("tau-token", payload.token);
            this.loggingIn = false;
            this.error = '';
        },
        authError(payload: { error: string }) {
            this.username = '';
            this.token = '';
            this.loggingIn = false;
            this.error = payload.error;
        },
    }
});