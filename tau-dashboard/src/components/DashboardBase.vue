<template>
  <div class="layout-container">
    <!-- <div class="layout-top-bar">
      <Button
        label="Logout"
        type="button"
        class="p-button-raised p-button-secondary"
        @click="logout()"
      />
    </div> -->
    <top-bar @logout="logout()"></top-bar>
    <div class="layout-side-bar"></div>
    <div class="layout-content">
      <router-view></router-view>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

import TopBar from './layout/TopBar.vue';

export default defineComponent({
  name: 'Dashboard',
  components: {
    TopBar,
  },
  setup() {
    const store = useStore();
    const router = useRouter();

    async function logout() {
      await store.dispatch('auth/logout');
      router.replace('/login');
    }

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

  .layout-side-bar {
    position: fixed;
    width: 250px;
    height: 100%;
    z-index: 999;
    overflow-y: auto;
    background-color: var(--bluegray-700);
  }

  .layout-content {
    padding: 70px 2rem 2rem 2rem;
    margin-left: 250px;
  }
}
</style>
