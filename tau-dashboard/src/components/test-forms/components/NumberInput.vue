<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <InputNumber
        v-model="inputValue"
        :placeholder="label"
        @input="onChange"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';

export default defineComponent({
  name: 'NumberInput',
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
    const inputValue = ref<string>();

    function onChange(event: any) {
      updateModel(event.value);
    }

    function updateModel(newValue: any) {
      emit('update:value', newValue);
    }

    return {
      onChange,
      inputValue,
    };
  },
});
</script>
