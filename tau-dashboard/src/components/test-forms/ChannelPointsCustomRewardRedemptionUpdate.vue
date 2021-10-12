<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Points Custom Reward Redemption Update"
    :modal="true"
    :closable="false"
  >
    <twitch-user
      v-model:valueId="testData.user_id"
      v-model:valueName="testData.user_name"
      v-model:valueLogin="testData.user_login"
      label="User"
    ></twitch-user>
    <reward-select
      v-model:value="testData.reward"
      :queuedOnly="true"
      label="Reward"
    >
    </reward-select>
    <emote-message
      v-if="testData?.reward?.is_user_input_required"
      v-model:value="testData.user_input"
      label="User Input"
    ></emote-message>
    <point-redemption-status-select
      v-model:value="testData.status"
      label="Status"
    ></point-redemption-status-select>
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
import RewardSelect from './components/RewardSelect.vue';
import EmoteMessage from './components/EmoteMessage.vue';
import PointRedemptionStatusSelect from './components/PointRedemptionStatusSelect.vue';
import { Reward } from './components/RewardSelect.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';
import { TwitchMessage } from './components/EmoteMessage.vue';
import { v4 as uuidv4 } from 'uuid';

interface RewardRedemptionData {
  id: string;
  reward: Reward | null;
  status: string;
  user_id: string;
  user_name: string;
  user_login: string;
  user_input: string | TwitchMessage;
  redeemed_at: string;
  broadcaster_user_id: string;
  broadcaster_user_name: string;
  broadcaster_user_login: string;
}

export default defineComponent({
  name: 'ChannelChannelPointsCustomRewardRedemptionUpdate',
  components: {
    BroadcasterInfo,
    TwitchUser,
    RewardSelect,
    EmoteMessage,
    PointRedemptionStatusSelect,
  },
  setup() {
    const store = useStore();
    const display = ref(true);
    const testData = reactive<RewardRedemptionData>({
      id: '',
      reward: null,
      status: 'fulfilled',
      user_id: '',
      user_name: '',
      user_login: '',
      user_input: '',
      redeemed_at: '',
      broadcaster_user_id: '',
      broadcaster_user_name: '',
      broadcaster_user_login: '',
    });

    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };
    const submit = () => {
      const payload: RewardRedemptionData = {
        ...testData,
        id: uuidv4(),
        reward: testData.reward
          ? {
              id: testData.reward.id,
              cost: testData.reward.cost,
              title: testData.reward.title,
              prompt: testData.reward.prompt,
            }
          : null,
        redeemed_at: new Date().toISOString(),
      };

      if (testData.reward?.is_user_input_required) {
        if (typeof testData.user_input !== 'string') {
          payload.user_input = testData.user_input.text;
        } else {
          payload.user_input = testData.user_input;
        }
      } else {
        payload.user_input = '';
      }
      api$.tau.post(
        'twitch-events/channel-channel_points_custom_reward_redemption-update/test',
        payload,
      );
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
