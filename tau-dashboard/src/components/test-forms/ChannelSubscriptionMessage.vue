<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Subscription Message"
    :modal="true"
    :closable="false"
    style="width: 450px"
  >
    <twitch-user
      v-model:valueId="testData.user_id"
      v-model:valueName="testData.user_name"
      v-model:valueLogin="testData.user_login"
      label="User"
    ></twitch-user>
    <emote-message
      v-model:value="testData.message"
      label="Message"
    ></emote-message>
    <sub-tier-select
      v-model:value="testData.tier"
      label="Tier"
    ></sub-tier-select>
    <number-input
      v-model:value="testData.cumulative_months"
      label="Cumulative Months"
    ></number-input>
    <toggle v-model:value="showStreak" label="Show Streak?"></toggle>
    <number-input
      v-if="showStreak"
      v-model:value="testData.streak_months"
      label="Streak Months"
    ></number-input>
    <number-input
      v-model:value="testData.duration_months"
      label="Duration Months"
    ></number-input>
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
import EmoteMessage, { TwitchMessage } from './components/EmoteMessage.vue';
import SubTierSelect from './components/SubTierSelect.vue';
import NumberInput from './components/NumberInput.vue';
import Toggle from './components/Toggle.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

interface ChannelSubscriptionMessageData {
  user_id: string;
  user_name: string;
  user_login: string;
  broadcaster_user_id: string;
  broadcaster_user_name: string;
  broadcaster_user_login: string;
  tier: string;
  message: TwitchMessage;
  cumulative_months: number;
  streak_months: number | null;
  duration_months: number;
}

export default defineComponent({
  name: 'ChannelSubscriptionMessage',
  components: {
    BroadcasterInfo,
    TwitchUser,
    EmoteMessage,
    SubTierSelect,
    NumberInput,
    Toggle,
  },
  setup() {
    const store = useStore();
    const test = ref('test');
    const display = ref(true);
    const showStreak = ref(true);
    const testData = reactive<ChannelSubscriptionMessageData>({
      user_id: '',
      user_name: '',
      user_login: '',
      broadcaster_user_id: '',
      broadcaster_user_name: '',
      broadcaster_user_login: '',
      tier: '1000',
      message: {
        text: '',
        emotes: [],
      },
      cumulative_months: 0,
      streak_months: 0,
      duration_months: 0,
    });

    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };
    const catChange = (ev: any) => {
      console.log(ev);
    };
    const submit = () => {
      console.log(testData);
      if (!showStreak.value) {
        testData.streak_months = null;
      }
      api$.tau.post(
        'twitch-events/channel-subscription-message/test',
        testData,
      );
    };

    return {
      showStreak,
      test,
      testData,
      close,
      submit,
      catChange,
      display,
    };
  },
});
</script>
