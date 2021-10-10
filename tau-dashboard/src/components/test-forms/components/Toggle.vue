<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <InputSwitch
        v-model="inputValue"
        :placeholder="label"
        @change="onChange"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, PropType, onMounted } from 'vue';

export default defineComponent({
  name: 'Toggle',
  emits: ['update:value'],
  props: {
    value: {
      type: Boolean,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const inputValue = ref<boolean>(false);

    function onChange(event: any) {
      updateModel(event, inputValue.value);
    }

    function updateModel(event: any, value: boolean) {
      emit('update:value', value);
      //emit('change', { originalEvent: event, value: value });
    }

    onMounted(() => {
      inputValue.value = props.value;
    });

    return {
      onChange,
      inputValue,
    };
  },
});
</script>
