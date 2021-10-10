<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <Dropdown
        v-model="inputValue.reward"
        :options="rewards"
        optionLabel="title"
        dataKey="id"
        placeholder="Select a reward"
        @change="onChange"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive, PropType } from 'vue';
import { useStore } from 'vuex';
import tau from '@/services/tau-apis';

export interface Reward {
  id: string;
  cost: number;
  title: string;
  prompt: string;
  is_user_input_required?: boolean;
  should_redemptions_skip_request_queue?: boolean;
}

export interface RewardsResponse {
  data: Reward[];
  pagination: { cursor: string };
}

export default defineComponent({
  name: 'RewardSelect',
  emits: ['update:value'],
  props: {
    value: {
      type: null as unknown as PropType<Reward>,
      required: false,
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const store = useStore();
    const inputValue = reactive<{ reward: Reward | null }>({
      reward: null,
    });
    const rewards = ref<Reward[]>([]);
    function onChange(event: any) {
      updateModel(inputValue.reward);
    }

    function updateModel(reward: Reward | null) {
      console.log(reward);
      emit('update:value', {
        id: reward.id,
        cost: reward.cost,
        title: reward.title,
        prompt: reward.prompt,
        is_user_input_required: reward.is_user_input_required,
        should_redemptions_skip_request_queue:
          reward.should_redemptions_skip_request_queue,
      });
    }

    onMounted(async () => {
      await store.dispatch('broadcaster/load');
      const broadcaster_id = store.getters['broadcaster/data'].id;
      const rewardsResponse = await tau.helix.get<RewardsResponse>(
        `channel_points/custom_rewards`,
        {
          broadcaster_id,
        },
      );
      rewards.value = rewardsResponse.data;
    });

    return {
      onChange,
      inputValue,
      rewards,
    };
  },
});
</script>
