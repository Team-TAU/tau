<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Subscription End"
    :modal="true"
    :closable="false"
  >
    <twitch-user
      v-model:valueId="testData.user_id"
      v-model:valueName="testData.user_name"
      v-model:valueLogin="testData.user_login"
      label="User"
    ></twitch-user>
    <sub-tier-select
      v-model:value="testData.tier"
      label="Tier"
    ></sub-tier-select>
    <toggle v-model:value="testData.is_gift" label="Is Gift?"></toggle>
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
import SubTierSelect from './components/SubTierSelect.vue';
import Toggle from './components/Toggle.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

export default defineComponent({
  name: 'ChannelSubscriptionEnd',
  components: {
    BroadcasterInfo,
    TwitchUser,
    SubTierSelect,
    Toggle,
  },
  setup() {
    const store = useStore();
    const display = ref(true);
    const testData = reactive({
      user_id: '',
      user_name: '',
      user_login: '',
      broadcaster_user_id: '',
      broadcaster_user_name: '',
      broadcaster_user_login: '',
      tier: '',
      is_gift: false,
    });

    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };

    const submit = () => {
      api$.tau.post('twitch-events/channel-subscription-end/test', testData);
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
