<template>
  <component :is="view?.lookup_name"></component>
</template>

<script lang="ts">
import { computed, defineComponent } from 'vue';
import { useStore } from 'vuex';
import ChannelUpdate from './ChannelUpdate.vue';
import ChannelFollow from './ChannelFollow.vue';
import ChannelCheer from './ChannelCheer.vue';
import ChannelGoalBegin from './ChannelGoalBegin.vue';
import ChannelGoalEnd from './ChannelGoalEnd.vue';
import ChannelGoalProgress from './ChannelGoalProgress.vue';
import ChannelSubscriptionMessage from './ChannelSubscriptionMessage.vue';
import ChannelBan from './ChannelBan.vue';
import ChannelUnban from './ChannelUnban.vue';
import ChannelRaid from './ChannelRaid.vue';
import ChannelChannelPointsCustomRewardRedemptionAdd from './ChannelPointsCustomRewardRedemptionAdd.vue';
import ChannelChannelPointsCustomRewardRedemptionUpdate from './ChannelPointsCustomRewardRedemptionUpdate.vue';
import ChannelSubscribe from './ChannelSubscribe.vue';
import ChannelSubscriptionEnd from './ChannelSubscriptionEnd.vue';
import ChannelSubscriptionGift from './ChannelSubscriptionGift.vue';
export default defineComponent({
  name: 'Test Form Dialog',
  components: {
    ChannelUpdate,
    ChannelBan,
    ChannelFollow,
    ChannelCheer,
    ChannelGoalBegin,
    ChannelGoalEnd,
    ChannelGoalProgress,
    ChannelRaid,
    ChannelChannelPointsCustomRewardRedemptionAdd,
    ChannelChannelPointsCustomRewardRedemptionUpdate,
    ChannelSubscribe,
    ChannelSubscriptionEnd,
    ChannelSubscriptionGift,
    ChannelSubscriptionMessage,
    ChannelUnban,
  },
  setup() {
    const store = useStore();

    const view = computed(function () {
      return store.getters['UI/testFormView'];
    });

    return {
      view,
    };
  },
});
</script>
