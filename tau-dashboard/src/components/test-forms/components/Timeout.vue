<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <SelectButton
        v-model="inputValue"
        :options="timeoutOptions"
        optionLabel="name"
        optionValue="value"
        :multiple="false"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'Timeout',
  emits: ['update:value'],
  props: {
    value: {
      type: Number,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const inputValue = ref<number>(0);
    const timeoutOptions = ref([
      { name: '10s', value: 10 },
      { name: '1m', value: 60 },
      { name: '10m', value: 600 },
      { name: '30m', value: 1800 },
    ]);

    function onChange(event: any) {
      updateModel(event.value);
    }

    function updateModel(newValue: any) {
      emit('update:value', newValue);
    }

    return {
      onChange,
      inputValue,
      timeoutOptions,
    };
  },
});
</script>
