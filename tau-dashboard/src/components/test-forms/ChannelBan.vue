<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Ban"
    :modal="true"
    :closable="false"
    style="width: 450px"
  >
    <twitch-user
      v-model:valueId="testData.user_id"
      v-model:valueName="testData.user_name"
      v-model:valueLogin="testData.user_login"
      label="Banned User"
    ></twitch-user>
    <moderator-select
      v-model:valueId="testData.moderator_user_id"
      v-model:valueName="testData.moderator_user_name"
      v-model:valueLogin="testData.moderator_user_login"
      label="Moderator"
    ></moderator-select>
    <text-input v-model:value="testData.reason" label="Reason"></text-input>
    <toggle v-model:value="testData.is_permanent" label="Is Permanent"></toggle>
    <timeout
      v-if="!testData.is_permanent"
      v-model:value="timeoutSeconds"
      label="Timeout"
    ></timeout>
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
import { addSeconds, format } from 'date-fns';
import { defineComponent, reactive, ref } from 'vue';
import BroadcasterInfo from './components/BroadcasterInfo.vue';
import TwitchUser from './components/TwitchUser.vue';
import ModeratorSelect from './components/ModeratorSelect.vue';
import TextInput from './components/TextInput.vue';
import Toggle from './components/Toggle.vue';
import Timeout from './components/Timeout.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

export default defineComponent({
  name: 'ChannelBan',
  components: {
    BroadcasterInfo,
    TwitchUser,
    ModeratorSelect,
    TextInput,
    Toggle,
    Timeout,
  },
  setup() {
    const store = useStore();
    const display = ref(true);
    const timeoutSeconds = ref(0);
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
      reason: '',
      ends_at: '',
      is_permanent: false,
    });

    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };

    const submit = () => {
      if (!testData.is_permanent) {
        // calculate ends_at
        const date = addSeconds(new Date(), timeoutSeconds.value);
        testData.ends_at = date.toISOString();
      }
      api$.tau.post('twitch-events/channel-ban/test', testData);
      // display.value = false;
    };

    return {
      testData,
      timeoutSeconds,
      close,
      submit,
      display,
    };
  },
});
</script>
