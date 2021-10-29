<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <span class="p-input-icon-right">
        <i
          class="pi pi-check"
          style="color: var(--green-500)"
          v-if="validUser"
        />
        <i
          class="pi pi-times"
          style="color: var(--pink-500)"
          v-if="!validUser"
        />
        <InputText
          v-model="inputValue"
          :placeholder="label"
          @input="debounceGetUser()"
        />
      </span>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import _ from 'lodash';
import tau from '@/services/tau-apis';

interface TwitchUserData {
  broadcaster_type: string;
  created_at: string;
  description: string;
  display_name: string;
  id: string;
  login: string;
  offline_image_url: string;
  profile_image_url: string;
  type: string;
  view_count: number;
}

interface TwitchUserResponse {
  data: TwitchUserData[];
}

export default defineComponent({
  name: 'TwitchUser',
  emits: ['update:valueId', 'update:valueName', 'update:valueLogin'],
  props: {
    valueId: {
      type: String,
      default: '',
    },
    valueName: {
      type: String,
      default: '',
    },
    valueLogin: {
      type: String,
      default: '',
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const inputValue = ref<string>();
    const validUser = ref<boolean>(false);

    const onChange = (ev: any) => {
      console.log(ev);
    };

    const debounceGetUser: any = _.debounce(() => {
      getUser();
    }, 400);

    async function getUser() {
      const input: string = inputValue?.value?.toLowerCase() || '';
      const userResp = await tau.helix.get<TwitchUserResponse>(`users`, {
        login: input,
      });
      let id = null;
      let display_name = null;
      let login = null;
      if (userResp.data.length > 0) {
        console.log('here');
        const user = userResp.data[0];
        id = user.id;
        display_name = user.display_name;
        login = user.login;
        validUser.value = true;
      } else {
        validUser.value = false;
      }
      updateModel(id, display_name, login);
    }

    function updateModel(
      id: string | undefined | null,
      name: string | undefined | null,
      login: string | undefined | null,
    ) {
      console.log('emitting', id, name, login);
      emit('update:valueId', id);
      emit('update:valueName', name);
      emit('update:valueLogin', login);
    }

    return {
      validUser,
      inputValue,
      debounceGetUser,
    };
  },
});
</script>
