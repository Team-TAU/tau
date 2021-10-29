<template>
  <div class="layout-container">
    <top-bar @logout="logout()"></top-bar>
    <side-bar></side-bar>
    <div class="layout-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

import TopBar from './layout/TopBar.vue';
import SideBar from './layout/SideBar.vue';

export default defineComponent({
  name: 'Dashboard',
  components: {
    TopBar,
    SideBar,
  },
  setup() {
    const store = useStore();
    const router = useRouter();

    async function logout() {
      await store.dispatch('auth/logout');
      router.replace('/login');
    }

    async function fetchEventSubscriptions() {
      await store.dispatch('eventSubscriptions/loadAll');
    }

    onMounted(fetchEventSubscriptions);

    return {
      logout,
    };
  },
});
</script>

<style lang="scss">
.layout-container {
  padding: 0;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 100vh;

  .layout-content {
    padding: 70px 2rem 2rem 2rem;
    margin-left: 250px;
  }
}
</style>
