<template>
  <div class="layout-top-bar">
    <Button label="Logout" type="button" class="p-button-raised p-button-secondary" @click="logout()" />
  </div>
</template>

<script lang="ts">
import { useAuthStore } from '@/stores/auth';
import { defineComponent } from 'vue';
import { useRouter } from 'vue-router';

export default defineComponent({
  name: 'TopBar',
  setup(props, context) {
    const userStore = useAuthStore();
    const router = useRouter();

    function logout() {
      userStore.logout();
      router.replace("/login");
    }

    return {
      logout,
    };
  },
});
</script>

<style lang="scss">
.layout-top-bar {
  position: fixed;
  height: 50px;
  padding: 0.3em 1em 0em 1em;
  z-index: 999;
  right: 0;
  text-align: right;
  background-color: #425a70;
  color: #eeeeee;
  border-bottom: 1px solid #eeeeee;

  left: 250px;
}
</style>
