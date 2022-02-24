<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Cheer"
    :modal="true"
    @hide="hide"
    :closable="false"
  >
    <twitch-user
      v-model:valueId="testData.user_id"
      v-model:valueName="testData.user_name"
      v-model:valueLogin="testData.user_login"
      label="User"
    ></twitch-user>
    <broadcaster-info
      v-model:valueUserId="testData.broadcaster_user_id"
      v-model:valueUserLogin="testData.broadcaster_user_login"
      v-model:valueUserName="testData.broadcaster_user_name"
    ></broadcaster-info>
    <text-input v-model:value="testData.bits" label="Bits"></text-input>
    <text-input v-model:value="testData.message" label="Message"></text-input>
    <toggle v-model:value="testData.is_anonymous" label="Anonymous?"></toggle>

    <template #footer>
      <Button
        label="Cancel"
        icon="pi pi-times"
        @click="close"
        class="p-button-text"
      />
      <Button
        label="Submit"
        icon="pi pi-check"
        @click="submit"
        class="p-button-text"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { defineComponent, reactive, ref } from 'vue';
import BroadcasterInfo from './components/BroadcasterInfo.vue';
import TwitchUser from './components/TwitchUser.vue';
import TextInput from './components/TextInput.vue';
import Toggle from './components/Toggle.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

interface CheerData {
  is_anonymous: boolean;
  user_id: string | null;
  user_name: string | null;
  user_login: string | null;
  broadcaster_user_id: string;
  broadcaster_user_name: string;
  broadcaster_user_login: string;
  bits: number;
  message: string;
}

export default defineComponent({
  name: 'ChannelCheer',
  components: {
    BroadcasterInfo,
    TwitchUser,
    TextInput,
    Toggle,
  },
  setup() {
    const store = useStore();
    const test = ref('test');
    const display = ref(true);
    const testData = reactive<CheerData>({
      is_anonymous: false,
      user_id: '',
      user_name: '',
      user_login: '',
      broadcaster_user_id: '',
      broadcaster_user_name: '',
      broadcaster_user_login: '',
      bits: 0,
      message: '',
    });

    const hide = () => {
      console.log('Hide!');
    };
    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };
    const catChange = (ev: any) => {
      console.log(ev);
    };
    const submit = () => {
      if (testData.is_anonymous) {
        testData.user_id = null;
        testData.user_name = null;
        testData.user_login = null;
      }
      api$.tau.post('twitch-events/channel-cheer/test', testData);
      close();
    };

    return {
      test,
      testData,
      close,
      submit,
      catChange,
      display,
      hide,
    };
  },
});
</script>
