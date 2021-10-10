<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Raid"
    :modal="true"
    :closable="false"
  >
    <twitch-user
      v-model:valueId="testData.from_broadcaster_user_id"
      v-model:valueName="testData.from_broadcaster_user_name"
      v-model:valueLogin="testData.from_broadcaster_user_login"
      label="Raider"
    ></twitch-user>
    <number-input
      v-model:value="testData.viewers"
      label="Viewers"
    ></number-input>
    <broadcaster-info
      v-model:valueUserId="testData.to_broadcaster_user_id"
      v-model:valueUserLogin="testData.to_broadcaster_user_login"
      v-model:valueUserName="testData.to_broadcaster_user_name"
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
import NumberInput from './components/NumberInput.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

export default defineComponent({
  name: 'ChannelRaid',
  components: {
    BroadcasterInfo,
    TwitchUser,
    NumberInput,
  },
  setup() {
    const store = useStore();
    const display = ref(true);
    const testData = reactive({
      from_broadcaster_user_id: '',
      from_broadcaster_user_name: '',
      from_broadcaster_user_login: '',
      to_broadcaster_user_id: '',
      to_broadcaster_user_name: '',
      to_broadcaster_user_login: '',
      viewers: 0,
    });

    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };
    const submit = () => {
      api$.tau.post('twitch-events/channel-raid/test', testData);
    };

    return {
      testData,
      close,
      submit,
      display,
    };
  },
});
</script>
