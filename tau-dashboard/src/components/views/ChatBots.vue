<template>
  <h1>Chat Bots</h1>
  <div class="grid">
    <div class="col-12">
      <Panel class="dark-header" header="Chat Bots Status">
        <template #icons>
          <button
            class="p-panel-header-icon p-link p-mr-2"
            @click="addChatBot()"
          >
            <span class="pi pi-plus"></span>
          </button>
        </template>
        <DataTable :value="data" stripedRows>
          <Column field="user_name" header="Bot Name">
            <template #body="{ data }">
              <strong
                >{{ data.user_name }} [
                <a @click="addChannel(data)">Add</a>
                <Chip
                  removable
                  v-for="channel of data.channels"
                  v-bind:key="channel.id"
                  @remove="deleteChannel(channel)"
                  >{{ channel.channel }}</Chip
                >
                ]</strong
              >
            </template>
          </Column>
          <Column
            field="delete"
            headerStyle="width: 4rem; text-align: center"
            header=""
          >
            <template #body="{ data }">
              <Button
                icon="pi pi-trash"
                class="p-button-rounded p-button-danger p-button-text"
                @click="deleteBot(data)"
              />
            </template>
          </Column>
        </DataTable>
        <h2 v-if="data.length === 0">No chat bots created.</h2>
      </Panel>
    </div>
  </div>
  <Toast />
  <Dialog
    v-model:visible="channelAddModal"
    header="Add Channel"
    :modal="true"
    :closeable="true"
  >
    <twitch-user
      v-model:valueLogin="newChannel.channel"
      label="User"
    ></twitch-user>
    <template #footer>
      <Button
        label="Cancel"
        icon="pi pi-times"
        @click="closeAddForm"
        class="p-button-text"
      />
      <Button
        label="Create Channel"
        icon="pi pi-save"
        @click="createChannel()"
        class="p-button-text"
      />
    </template>
  </Dialog>
  <Dialog
    v-model:visible="displayAddModal"
    header="Add Chat Bot"
    :modal="true"
    :closable="false"
    style="width: 85%"
  >
    <p>
      Click "Copy to Clipboard" below then paste the url in another browser
      instance, and authenticate as the bot account.
    </p>
    <div class="field grid">
      <label class="col-fixed" style="width: 140px">Auth URL:</label>
      <div class="col">
        <InputText v-model="url" disabled style="width: 100%" />
      </div>
    </div>
    <template #footer>
      <Button
        label="Cancel"
        icon="pi pi-times"
        @click="closeAddForm"
        class="p-button-text"
      />
      <Button
        label="Copy URL"
        icon="pi pi-copy"
        @click="copyUrl"
        class="p-button-text"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import { ChatBot, ChatBotChannel, ChatBotVM } from '@/models/chat-bot';
import {
  computed,
  defineComponent,
  inject,
  onMounted,
  reactive,
  ref,
} from 'vue';
import { useStore } from 'vuex';
import TwitchUser from '../test-forms/components/TwitchUser.vue';
import { useToast } from 'primevue/usetoast';
import Toast from 'primevue/toast';

import api$ from '@/services/tau-apis';
import { ChatBotStatusWsService } from '@/services/tau-api-ws';

export default defineComponent({
  name: 'ChatBot',
  components: {
    TwitchUser,
    Toast,
  },
  setup() {
    const store = useStore();
    const toast = useToast();
    const data = computed(() => {
      const cb = store.getters['chatBots/all'] as ChatBot[];
      const channels = store.getters['chatBotChannels/all'] as ChatBotChannel[];
      return cb.map(
        (chatBot: ChatBot): ChatBotVM => ({
          ...chatBot,
          channels: channels
            ? channels.filter((channel) => channel.chat_bot === chatBot.id)
            : [],
        }),
      );
    });

    const displayAddModal = ref(false);
    const channelAddModal = ref(false);

    const url = ref('Loading...');

    const chatBotStatusWs = inject('chatBotStatusWs') as ChatBotStatusWsService;

    const newBot = reactive({
      user_id: '',
      user_name: '',
      user_login: '',
    });

    const newChannel: ChatBotChannel = reactive({
      chat_bot: '',
      channel: '',
    });

    function addChatBot() {
      url.value = 'Loading...';
      api$.tau
        .get<{ url: string }>('chat-bots/twitch-auth-link')
        .then((resp) => {
          url.value = resp.url;
        });
      displayAddModal.value = true;
    }

    function closeAddForm() {
      displayAddModal.value = false;
    }

    function copyUrl() {
      navigator.clipboard.writeText(url.value).then(() => {
        console.log('copied to clipboard');
        toast.add({
          severity: 'info',
          summary: 'Clipboard',
          detail:
            'Twitch Auth URL copied to your clipboard.  Please paste in another browser instance, and authenticate as the bot account.',
          life: 10000,
        });
        displayAddModal.value = false;
      });
    }

    const deleteBot = async (bot: ChatBot) => {
      await store.dispatch('chatBots/delete', bot);
    };

    const fetchChatBots = async () => {
      chatBotStatusWs.connect();
      await store.dispatch('chatBots/loadAll');
      await store.dispatch('chatBotChannels/loadAll');
    };

    const deleteChannel = async (channel: ChatBotChannel) => {
      await store.dispatch('chatBotChannels/delete', channel);
    };

    const addChannel = (bot: ChatBotVM) => {
      console.log('Adding Channel');
      newChannel.channel = '';
      newChannel.chat_bot = bot.id ? bot.id : '';
      channelAddModal.value = true;
    };

    const createChannel = async () => {
      newChannel.channel = `#${newChannel.channel}`;
      await store.dispatch('chatBotChannels/addOne', newChannel);
      channelAddModal.value = false;
    };

    onMounted(fetchChatBots);

    return {
      displayAddModal,
      channelAddModal,
      newBot,
      newChannel,
      data,
      url,
      copyUrl,
      addChatBot,
      closeAddForm,
      deleteBot,
      deleteChannel,
      addChannel,
      createChannel,
    };
  },
});
</script>
<style lang="scss" scoped>
p {
  font-size: 1.5rem;
}
</style>
