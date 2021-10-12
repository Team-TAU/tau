<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <Dropdown
        v-model="inputValue"
        :options="tiers"
        optionLabel="label"
        optionValue="value"
        placeholder="Select a status"
        @change="onChange"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'PointRedemptionStatusSelect',
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
    const tiers = ref([
      { value: 'fulfilled', label: 'Fulfilled' },
      { value: 'canceled', label: 'Canceled' },
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
      tiers,
    };
  },
});
</script>
