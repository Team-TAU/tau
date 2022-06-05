<template>
  <router-view />
</template>

<script lang="ts">
import { useStore } from 'vuex';
import { defineComponent, provide } from 'vue';
import {
  TauStatusWsService,
  TauTwitchEventWsService,
  ChatBotStatusWsService,
} from './services/tau-api-ws';

export default defineComponent({
  name: 'App',
  setup() {
    const store = useStore();

    const tauStatusWs = new TauStatusWsService(store);
    const twitchEventWs = new TauTwitchEventWsService(store);
    const chatBotStatusWs = new ChatBotStatusWsService(store);
    provide('tauStatusWs', tauStatusWs);
    provide('twitchEventWs', twitchEventWs);
    provide('chatBotStatusWs', chatBotStatusWs);

    return {};
  },
});
</script>

<style lang="scss">
@import '@/assets/scss/main.scss';
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
}
</style>
