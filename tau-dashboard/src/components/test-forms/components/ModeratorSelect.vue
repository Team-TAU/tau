<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <Dropdown
        v-model="inputValue.user"
        :options="moderators"
        optionLabel="user_name"
        dataKey="user_id"
        placeholder="Select a moderator"
        @change="onChange"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, onMounted, reactive } from 'vue';
import { useStore } from 'vuex';
import tau from '@/services/tau-apis';

export interface Moderator {
  user_id: string;
  user_login: string;
  user_name: string;
}

export interface ModeratorResponse {
  data: Moderator[];
  pagination: { cursor: string };
}

export default defineComponent({
  name: 'ModeratorInput',
  emits: ['update:valueId', 'update:valueName', 'update:valueLogin'],
  props: {
    valueId: {
      type: String,
      required: true,
    },
    valueName: {
      type: String,
      required: true,
    },
    valueLogin: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const store = useStore();
    const inputValue = reactive<{ user: Moderator }>({
      user: {
        user_id: '',
        user_login: '',
        user_name: '',
      },
    });
    const moderators = ref<Moderator[]>([]);
    function onChange(event: any) {
      console.log(inputValue);
      console.log(event);
      updateModel(
        inputValue.user.user_id,
        inputValue.user.user_name,
        inputValue.user.user_login,
      );
    }

    function updateModel(id: string, name: string, login: string) {
      emit('update:valueId', id);
      emit('update:valueName', name);
      emit('update:valueLogin', login);
    }

    onMounted(async () => {
      const broadcaster_id = store.getters['broadcaster/data'].id;
      const moderatorsResponse = await tau.helix.get<ModeratorResponse>(
        `moderation/moderators`,
        {
          broadcaster_id,
        },
      );
      moderators.value = moderatorsResponse.data;
    });

    return {
      onChange,
      inputValue,
      moderators,
    };
  },
});
</script>
