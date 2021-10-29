<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Follow"
    :modal="true"
    @hide="hide"
    :closable="false"
  >
    <twitch-user
      v-model:valueId="testData.user_id"
      v-model:valueName="testData.user_name"
      v-model:valueLogin="testData.user_login"
      label="User"
    ></twitch-user>
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
import { format } from 'date-fns';
import { defineComponent, reactive, ref } from 'vue';
import BroadcasterInfo from './components/BroadcasterInfo.vue';
import TwitchUser from './components/TwitchUser.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

export default defineComponent({
  name: 'ChannelFollow',
  components: {
    BroadcasterInfo,
    TwitchUser,
  },
  setup() {
    const store = useStore();
    const test = ref('test');
    const display = ref(true);
    const testData = reactive({
      user_id: '',
      user_name: '',
      user_login: '',
      followed_at: '',
      broadcaster_user_id: '',
      broadcaster_user_name: '',
      broadcaster_user_login: '',
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
      testData.followed_at = new Date().toISOString();
      api$.tau.post('twitch-events/channel-follow/test', testData);
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
