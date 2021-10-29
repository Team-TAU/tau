<template>
  <h1>Streamers List</h1>
  <div class="grid">
    <div class="col-6">
      <Panel class="dark-header" header="Streamer Status">
        <template #icons>
          <button
            class="p-panel-header-icon p-link p-mr-2"
            @click="addStreamer()"
          >
            <span class="pi pi-plus"></span>
          </button>
        </template>
        <DataTable :value="data" stripedRows>
          <Column
            field="streaming"
            headerStyle="width: 6rem; text-align: center"
            header="Status"
            bodyClass="text-center"
            headerClass="text-center"
          >
            <template #body="{ data }">
              <Button
                icon="pi pi-video"
                class="p-button-rounded p-button-success"
                v-if="data.streaming"
              />
              <Button
                icon="pi pi-times"
                class="p-button-rounded p-button-outlined not-streaming"
                v-if="!data.streaming"
              />
            </template>
          </Column>
          <Column field="twitch_username" header="Event">
            <template #body="{ data }">
              <strong>{{ data.twitch_username }}</strong>
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
                @click="deleteStreamer(data)"
              />
            </template>
          </Column>
        </DataTable>
        <h2 v-if="data.length === 0">No streamers watched.</h2>
      </Panel>
    </div>
    <div class="col-6">
      <Panel class="dark-header" header="Websocket Stream">
        <Accordion :multiple="true">
          <AccordionTab
            v-for="te in twitchEvents"
            :key="te.event_id"
            :header="twitchEventTitle(te)"
          >
            <div class="prism-container">
              <Prism language="json">{{ te }}</Prism>
            </div>
            <Button
              label="Replay"
              type="button"
              class="p-button-raised p-button-primary"
              v-if="te.origin === 'twitch' || te.origin === 'replay'"
              @click="replay(te)"
            />
          </AccordionTab>
        </Accordion>
      </Panel>
    </div>
  </div>
  <Dialog
    v-model:visible="displayAddModal"
    header="Add Streamer"
    :modal="true"
    :closable="false"
    style="width: 450px"
  >
    <twitch-user
      v-model:valueId="newStreamer.user_id"
      v-model:valueName="newStreamer.user_name"
      v-model:valueLogin="newStreamer.user_login"
      label="Streamer"
    ></twitch-user>
    <template #footer>
      <Button
        label="Cancel"
        icon="pi pi-times"
        @click="closeAddForm"
        class="p-button-text"
      />
      <Button
        label="Submit"
        icon="pi pi-check"
        @click="submitAddForm"
        class="p-button-text"
      />
    </template>
  </Dialog>
</template>

<script lang="ts">
import {
  defineComponent,
  computed,
  onMounted,
  inject,
  ref,
  reactive,
} from 'vue';
import { useStore } from 'vuex';
import TwitchUser from '../test-forms/components/TwitchUser.vue';
import _ from 'lodash';

import Prism from 'vue-prism-component';

import {
  TauStatusWsService,
  TauTwitchEventWsService,
} from '@/services/tau-api-ws';

import { TwitchEvent, eventTitleMap } from '@/models/twitch-event';
import { Broadcaster } from '@/models/broadcaster';
import { Streamer } from '@/models/streamer';

export default defineComponent({
  name: 'Streamers',
  components: { Prism, TwitchUser },
  setup() {
    const store = useStore();

    const data = computed(() => {
      return store.getters['streamers/all'] as Streamer[];
    });

    const displayAddModal = ref(false);

    const newStreamer = reactive({
      user_id: '',
      user_name: '',
      user_login: '',
    });

    const broadcaster = computed<Broadcaster>(() => {
      return store.getters['broadcaster/data'];
    });

    const twitchEvents = computed(() => {
      return store.getters['twitchEvents/all'];
    });

    const fetchEventSubscriptions = async () => {
      await store.dispatch('twitchEvents/loadAll');
      await store.dispatch('streamers/loadAll');
      await store.dispatch('broadcaster/load');
      tauStatusWs.connect();
      twitchEventWs.connect();
    };

    const tauStatusWs = inject('tauStatusWs') as TauStatusWsService;
    const twitchEventWs = inject('twitchEventWs') as TauTwitchEventWsService;

    onMounted(fetchEventSubscriptions);

    function closeAddForm() {
      displayAddModal.value = false;
      newStreamer.user_id = '';
      newStreamer.user_name = '';
      newStreamer.user_login = '';
    }

    function submitAddForm() {
      // do something
      const payload: Streamer = {
        twitch_username: newStreamer.user_name,
        disabled: false,
        streaming: false,
      };
      store.dispatch('streamers/create', payload);
      closeAddForm();
    }

    function addStreamer() {
      console.log('add streamer!');
      displayAddModal.value = true;
    }

    function deleteStreamer(streamer: Streamer) {
      console.log('delete streamer!', streamer);
      store.dispatch('streamers/delete', streamer);
    }

    function twitchEventTitle(twitchEvent: TwitchEvent) {
      const msgSource =
        twitchEvent.origin === 'replay'
          ? '[Replay] '
          : twitchEvent.origin === 'test'
          ? '[Test] '
          : '';
      return twitchEvent.event_type in eventTitleMap
        ? msgSource + eventTitleMap[twitchEvent.event_type](twitchEvent)
        : msgSource + eventTitleMap['default'](twitchEvent);
    }

    function replay(twitchEvent: TwitchEvent) {
      store.dispatch('twitchEvents/replay', twitchEvent);
    }

    return {
      data,
      broadcaster,
      twitchEvents,
      twitchEventTitle,
      replay,
      addStreamer,
      displayAddModal,
      newStreamer,
      closeAddForm,
      submitAddForm,
      deleteStreamer,
    };
  },
});
</script>

<style lang="scss">
.p-panel {
  &.dark-header {
    .p-panel-header {
      background-color: var(--bluegray-800) !important;
      color: var(--bluegray-50) !important;
    }
  }
}

.prism-container {
  width: 100%;
}

.not-streaming {
  color: var(--bluegray-100) !important;
  border-color: var(--bluegray-100) !important;
}
</style>
