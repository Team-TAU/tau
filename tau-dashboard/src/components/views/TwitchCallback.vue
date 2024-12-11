<template>
  <div class="container">
    <div class="login-panel">
      <img src="../../assets/img/logo-grey.png" class="logo" />
      <div class="p-fluid"></div>
    </div>
  </div>
</template>

<script lang="ts">
import { useAuthStore } from "@/stores/auth";
import { defineComponent, onMounted } from "vue";
import { useRouter } from "vue-router";

export default defineComponent({
  name: "TwitchCallback",
  setup() {
    const router = useRouter();
    const authStore = useAuthStore();

    onMounted(async () => {
      try {
        const { code, state } = router.currentRoute.value.query;
        console.log({ code, state });
        const response = await window.fetch("/api/v1/auth/oauth", {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({ code, state })
        });
        console.log(response);
        if (response.status !== 200) {
          throw new Error(await response.text());
        }
        const { token, username } = await response.json();
        authStore.authSuccess({ token, username });
        router.replace("/");
      } catch (e: any) {
        authStore.authError({ error: e.message });
        router.replace("/login");
      }
    });
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
