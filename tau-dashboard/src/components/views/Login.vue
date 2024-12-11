<template>
  <div class="container">
    <div class="login-panel">
      <img src="../../assets/img/logo-grey.png" class="logo" />
      <p v-if="error">Error logging in: {{ error }}</p>
      <div class="p-fluid">
        <form @submit.prevent="login()">
          <Button label="Login via Twitch" class="mt-3" type="submit" />
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { useAuthStore } from "@/stores/auth";
import { storeToRefs } from "pinia";
import { defineComponent } from "vue";

export default defineComponent({
  name: "Login",
  setup() {
    const authStore = useAuthStore();

    const { error } = storeToRefs(authStore);

    async function login() {
      (window as any).location = "/api/v1/auth/login";
    }

    return {
      login,
      error,
    };
  },
});
</script>

<style lang="scss">
.container {
  display: grid;
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  margin: 0;
  place-items: center center;

  .login-panel {
    text-align: center;
    width: 225px;

    .logo {
      width: 150px;
      height: 150px;
      margin-bottom: 15px;
    }
  }
}
</style>
