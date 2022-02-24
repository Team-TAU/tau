<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Goal End"
    :modal="true"
    :closable="false"
    style="width: 450px"
  >
    <text-input
      v-model:value="testData.description"
      label="Description"
    ></text-input>
    <goal-type-select
      v-model:value="testData.type"
      label="Goal Type"
    ></goal-type-select>
    <number-input
      v-model:value="testData.target_amount"
      label="Target Amount"
    ></number-input>
    <number-input
      v-model:value="testData.current_amount"
      label="Current Amount"
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
import TextInput from './components/TextInput.vue';
import GoalTypeSelect from './components/GoalTypeSelect.vue';
import NumberInput from './components/NumberInput.vue';
import BroadcasterInfo from './components/BroadcasterInfo.vue';
import subDays from 'date-fns/subDays';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

export default defineComponent({
  name: 'ChannelUpdate',
  components: {
    TextInput,
    GoalTypeSelect,
    NumberInput,
    BroadcasterInfo,
  },
  setup() {
    const store = useStore();
    const display = ref(true);
    const testData = reactive({
      id: Array.from(Array(27), () =>
        Math.floor(Math.random() * 36).toString(36),
      ).join(''),
      type: 'follow',
      ended_at: new Date().toISOString(),
      started_at: subDays(new Date(), 1).toISOString(),
      description: '',
      is_achieved: false,
      target_amount: 30,
      current_amount: 23,
      broadcaster_user_id: '',
      broadcaster_user_name: '',
      broadcaster_user_login: '',
    });

    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };
    const submit = () => {
      testData.is_achieved = testData.current_amount >= testData.target_amount;
      api$.tau.post('twitch-events/channel-goal-end/test', testData);
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
