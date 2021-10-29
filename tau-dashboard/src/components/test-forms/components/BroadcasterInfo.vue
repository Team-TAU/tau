<template>
  <div></div>
</template>

<script lang="ts">
import { defineComponent, PropType, onMounted } from 'vue';
import { useStore } from 'vuex';

export default defineComponent({
  name: 'BroadcasterInfo',
  emits: [
    'update:valueUserId',
    'update:valueUserName',
    'update:valueUserLogin',
  ],
  props: {
    valueUserId: {
      type: String,
      required: true,
    },
    valueUserName: {
      type: String,
      required: true,
    },
    valueUserLogin: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const store = useStore();

    function updateModel(userId: string, userName: string, userLogin: string) {
      emit('update:valueUserId', userId);
      emit('update:valueUserName', userName);
      emit('update:valueUserLogin', userLogin);
    }

    onMounted(() => {
      console.log('broadcaster-info onMounted');
      //store.dispatch('broadcaster/load').then((res) => {
      updateModel(
        store.getters['broadcaster/data'].id,
        store.getters['broadcaster/data'].display_name,
        store.getters['broadcaster/data'].login,
      );
      //});
    });

    return {};
  },
});
</script>
