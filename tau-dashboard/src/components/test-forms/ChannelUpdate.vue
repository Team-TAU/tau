<template>
  <Dialog
    v-model:visible="display"
    header="Test Channel Update"
    :modal="true"
    :closable="false"
    style="width: 450px"
  >
    <twitch-category-select
      v-model:categoryId="testData.category_id"
      v-model:categoryName="testData.category_name"
      label="Category"
    ></twitch-category-select>
    <text-input v-model:value="testData.title" label="Title"></text-input>
    <language v-model:value="testData.language" label="Language"></language>
    <toggle v-model:value="testData.is_mature" label="Is Mature"></toggle>
    <broadcaster-info
      v-model:valueUserId="testData.broadcaster_user_id"
      v-model:valueUserLogin="testData.broadcaster_user_login"
      v-model:valueUserName="testData.broadcaster_user_name"
    ></broadcaster-info>
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
import TwitchCategorySelect from './components/TwitchCategorySelect.vue';
import TextInput from './components/TextInput.vue';
import Toggle from './components/Toggle.vue';
import Language from './components/Language.vue';
import BroadcasterInfo from './components/BroadcasterInfo.vue';

import api$ from '@/services/tau-apis';

import { useStore } from 'vuex';

export default defineComponent({
  name: 'ChannelUpdate',
  components: {
    TwitchCategorySelect,
    TextInput,
    Language,
    Toggle,
    BroadcasterInfo,
  },
  setup() {
    const store = useStore();
    const display = ref(true);
    const testData = reactive({
      title: '',
      language: '',
      is_mature: false,
      category_id: '',
      category_name: '',
      broadcaster_user_id: '',
      broadcaster_user_name: '',
      broadcaster_user_login: '',
    });

    const close = () => {
      store.dispatch('UI/clearTestFormView');
    };
    const catChange = (ev: any) => {
      console.log(ev);
    };
    const submit = () => {
      console.log(testData);
      api$.tau.post('twitch-events/channel-update/test', testData);
      display.value = false;
    };

    return {
      testData,
      close,
      submit,
      catChange,
      display,
    };
  },
});
</script>
