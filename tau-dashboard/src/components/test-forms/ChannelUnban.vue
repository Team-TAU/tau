<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Unban"
    :modal="true"
    @hide="hide"
    :closable="false"
  >
    <twitch-user
      v-model:valueId="testData.user_id"
      v-model:valueName="testData.user_name"
      v-model:valueLogin="testData.user_login"
      label="Unbanned User"
    ></twitch-user>
    <moderator-select
      v-model:valueId="testData.moderator_user_id"
      v-model:valueName="testData.moderator_user_name"
      v-model:valueLogin="testData.moderator_user_login"
      label="Moderator"
    ></moderator-select>
    <broadcaster-info
      v-model:valueUserId="testData.broadcaster_user_id"
      v-model:valueUserLogin="testData.broadcaster_user_login"
      v-model:valueUserName="testData.broadcaster_user_name"
    ></broadcaster-info>
    <template #footer>
      <Button
        label="Cancel"
        icon="pi pi-times"
        @click="close"
        class="p-button-text"
      />
      <Button
        label="Submit"
        icon="pi pi-check"
        @click="submit"
        class="p-button-text"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from 'vue';
import BroadcasterInfo from './components/BroadcasterInfo.vue';
import TwitchUser from './components/TwitchUser.vue';
import ModeratorSelect from './components/ModeratorSelect.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

export default defineComponent({
  name: 'ChannelUnban',
  components: {
    BroadcasterInfo,
    TwitchUser,
    ModeratorSelect,
  },
  setup() {
    const store = useStore();
    const test = ref('test');
    const display = ref(true);
    const testData = reactive({
      user_id: '',
      user_name: '',
      user_login: '',
      broadcaster_user_id: '',
      broadcaster_user_name: '',
      broadcaster_user_login: '',
      moderator_user_id: '',
      moderator_user_name: '',
      moderator_user_login: '',
    });

    const hide = () => {
      console.log('Hide!');
    };
    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };
    const catChange = (ev: any) => {
      console.log(ev);
    };
    const submit = () => {
      api$.tau.post('twitch-events/channel-unban/test', testData);
      // display.value = false;
    };

    return {
      test,
      testData,
      close,
      submit,
      catChange,
      display,
      hide,
    };
  },
});
</script>
