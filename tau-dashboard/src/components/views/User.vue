<template>
  <h1>User Control Panel</h1>
  <Panel class="dark-header" header="User Settings">
    <div class="item">
      <div class="label">Auth Token:</div>
      <div class="buttons">
        <Button
          label="View Token"
          class="p-button-raised"
          @click="openTokenModal()"
        />
        <Button
          label="Reset Token"
          class="p-button-raised p-button-danger"
          @click="refreshToken()"
        />
      </div>
    </div>
  </Panel>

  <Dialog
    v-model:visible="displayTokenModal"
    header="Token"
    :modal="true"
    :closable="true"
    style="width: 450px"
  >
    {{ token }}
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import api$ from '@/services/tau-apis';

export default defineComponent({
  name: 'User',
  setup() {
    const displayTokenModal = ref(false);
    const token = ref('loading...');

    const refreshToken = async () => {
      token.value = 'refreshing...';
      displayTokenModal.value = true;
      const newTokenData = await api$.tau.post('tau-user-token/refresh/', {});
      localStorage.setItem('tau-token', newTokenData.token);
      token.value = newTokenData.token;
    };

    const openTokenModal = async () => {
      token.value = 'loading...';
      displayTokenModal.value = true;
      const tokenData = await api$.tau.get('tau-user-token/');
      token.value = tokenData.token;
    };

    return {
      token,
      displayTokenModal,
      refreshToken,
      openTokenModal,
    };
  },
});
</script>

<style lang="scss" scoped>
.label {
  font-size: 1.2em;
  font-weight: bold;
}

Button {
  margin: 2px;
}
</style>
