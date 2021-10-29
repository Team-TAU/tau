<template>
  <div class="layout-top-bar">
    <Button
      label="Logout"
      type="button"
      class="p-button-raised p-button-secondary"
      @click="logout()"
    />
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';
export default defineComponent({
  name: 'TopBar',
  setup(props, context) {
    const store = useStore();
    const router = useRouter();

    function logout() {
      context.emit('logout');
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
