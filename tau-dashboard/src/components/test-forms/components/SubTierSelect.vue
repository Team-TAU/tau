<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <Dropdown
        v-model="inputValue"
        :options="tiers"
        optionLabel="label"
        optionValue="value"
        placeholder="Select a tier"
        @change="onChange"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, PropType, onMounted } from 'vue';

export default defineComponent({
  name: 'SubTierSelect',
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
      { value: '1000', label: 'Tier 1' },
      { value: '2000', label: 'Tier 2' },
      { value: '3000', label: 'Tier 3' },
      { value: 'prime', label: 'Prime' },
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
