<template>
  <div class="container">
    <div class="login-panel">
      <img src="../../assets/img/logo-grey.png" class="logo" />
      <p v-if="error !== null">{{ error }}</p>
      <div class="p-fluid">
        <form @submit.prevent="login()">
          <span class="p-float-label mb-2">
            <InputText
              id="username"
              v-model="username"
              placeholder="Username"
              type="text"
            />
          </span>
          <span class="p-float-label">
            <Password
              v-model="password"
              placeholder="Password"
              :feedback="false"
            />
          </span>
          <Button label="Login" class="mt-3" type="submit" />
        </form>
      </div>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

export default defineComponent({
  name: 'Login',
  setup() {
    const store = useStore();
    const router = useRouter();

    const username = ref();
    const password = ref();

    const error = computed(function () {
      return store.getters['auth/error'];
    });

    async function login() {
      const success = await store.dispatch('auth/login', {
        username: username.value,
        password: password.value,
      });
      if (success) {
        router.replace('/');
      }
    }

    return {
      username,
      password,
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
