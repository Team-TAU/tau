<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Subscription Gift"
    :modal="true"
    :closable="false"
  >
    <toggle
      v-model:value="testData.is_anonymous"
      label="Is Anonymous?"
    ></toggle>
    <twitch-user
      v-if="!testData.is_anonymous"
      v-model:valueId="testData.user_id"
      v-model:valueName="testData.user_name"
      v-model:valueLogin="testData.user_login"
      label="Gifting User"
    ></twitch-user>
    <number-input
      v-model:value="testData.total"
      label="How Many?"
    ></number-input>
    <sub-tier-select
      v-model:value="testData.tier"
      label="Tier"
    ></sub-tier-select>
    <number-input
      v-if="!testData.is_anonymous"
      v-model:value="testData.cumulative_total"
      label="Cumulative Total"
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
import SubTierSelect from './components/SubTierSelect.vue';
import Toggle from './components/Toggle.vue';
import NumberInput from './components/NumberInput.vue';
import _ from 'lodash';
import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

export interface ChannelSubscriptionGiftEvent {
  user_id: string | null;
  user_login: string | null;
  user_name: string | null;
  broadcaster_user_id: string;
  broadcaster_user_login: string;
  broadcaster_user_name: string;
  total: number;
  tier: string;
  cumulative_total: number | null;
  is_anonymous: false;
}

interface Follower {
  from_id: string;
  from_login: string;
  from_name: string;
  to_id: string;
  to_login: string;
  to_name: string;
  followed_at: string;
}

interface FollowerResponse {
  total: number;
  data: Follower[];
  pagination: { cursor: string };
}

export default defineComponent({
  name: 'ChannelSubscriptionGift',
  components: {
    BroadcasterInfo,
    TwitchUser,
    SubTierSelect,
    Toggle,
    NumberInput,
  },
  setup() {
    const store = useStore();
    const display = ref(true);
    const testData = reactive<ChannelSubscriptionGiftEvent>({
      user_id: '',
      user_login: '',
      user_name: '',
      broadcaster_user_id: '',
      broadcaster_user_login: '',
      broadcaster_user_name: '',
      total: 0,
      tier: '',
      cumulative_total: 0,
      is_anonymous: false,
    });

    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };

    const submit = async () => {
      if (testData.is_anonymous) {
        testData.user_id = null;
        testData.user_login = null;
        testData.user_name = null;
        testData.cumulative_total = null;
      }
      const followerData = await api$.helix.get<FollowerResponse>(
        'users/follows',
        {
          to_id: testData.broadcaster_user_id,
          first: 100,
        },
      );
      const followers = _.shuffle(followerData.data);
      await api$.tau.post(
        'twitch-events/channel-subscription-gift/test',
        testData,
      );
      for (let i = 0; i < testData.total; i++) {
        const payload = {
          user_id: followers[i].from_id,
          user_name: followers[i].from_name,
          user_login: followers[i].from_login,
          broadcaster_user_id: testData.broadcaster_user_id,
          broadcaster_user_name: testData.broadcaster_user_name,
          broadcaster_user_login: testData.broadcaster_user_login,
          tier: testData.tier,
          is_gift: true,
        };
        await api$.tau.post('twitch-events/channel-subscribe/test', payload);
      }
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
