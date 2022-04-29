<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <Dropdown
        v-model="inputValue"
        :options="goalTypes"
        optionLabel="label"
        optionValue="value"
        placeholder="Select a goal type"
        @change="onChange"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, PropType, onMounted } from 'vue';

export default defineComponent({
  name: 'GoalTypeSelect',
  emits: ['update:value'],
  props: {
    value: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const inputValue = ref<string>();
    const goalTypes = ref([
      { value: 'follow', label: 'Follow' },
      { value: 'subscription', label: 'Subscription' },
    ]);
    function onChange(event: any) {
      updateModel(event.value);
    }

    function updateModel(val: any) {
      emit('update:value', val);
    }

    return {
      onChange,
      inputValue,
      goalTypes,
    };
  },
});
</script>
