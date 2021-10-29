<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <InputText v-model="inputValue" :placeholder="label" @change="onChange" />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, PropType } from 'vue';

export default defineComponent({
  name: 'TextInput',
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

    function onChange(event: any) {
      updateModel(event.target.value);
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
