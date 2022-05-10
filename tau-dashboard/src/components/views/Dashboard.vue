<template>
  <h1>{{ broadcaster?.display_name }}</h1>
  <div class="grid">
    <div class="col-6">
      <Panel class="dark-header" header="Event Subscriptions">
        <DataTable :value="data" stripedRows>
          <Column field="subscription_type" header="Event">
            <template #body="{ data }">
              <strong>{{ data.subscription_type }}</strong>
            </template>
          </Column>
          <Column
            field="status"
            headerStyle="width: 6rem; text-align: center"
            header="Status"
            bodyClass="text-center"
            headerClass="text-center"
          >
            <template #body="{ data }">
              <i
                class="pi pi-check text-green-500"
                v-if="data.status === 'CON'"
              ></i>
              <i
                class="pi pi-times text-orange-600"
                v-else-if="data.status === 'DIS'"
              ></i>
              <i
                class="pi pi-spin pi-spinner"
                v-else-if="data.status === 'CTG'"
              ></i>
            </template>
          </Column>
          <Column
            field="testing"
            headerStyle="width: 4rem; text-align: center"
            header=""
          >
            <template #body="{ data }">
              <Button
                class="p-button-sm"
                v-if="componentExists(data)"
                @click="openTestDialog(data)"
                >Test</Button
              >
            </template>
          </Column>
        </DataTable>
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
            <Button
              label="Replay Test"
              type="button"
              class="p-button-raised p-button-primary"
              v-if="te.origin === 'test'"
              @click="replayTest(te)"
            />
          </AccordionTab>
        </Accordion>
      </Panel>
    </div>
  </div>
  <TestForm></TestForm>
</template>

<script lang="ts">
import {
  defineComponent,
  computed,
  onMounted,
  inject,
  resolveComponent,
  ComponentOptions,
} from 'vue';
import { useStore } from 'vuex';
import _ from 'lodash';

import Prism from 'vue-prism-component';
import TestForm from '../test-forms/TestForm.vue';

import {
  TauStatusWsService,
  TauTwitchEventWsService,
} from '@/services/tau-api-ws';

import { TwitchEvent, eventTitleMap } from '@/models/twitch-event';
import { EventSubscription } from '@/models/event-subscription';
import { Broadcaster } from '@/models/broadcaster';

import api$ from '@/services/tau-apis';

export default defineComponent({
  name: 'Dashboard',
  components: { Prism, TestForm },
  setup() {
    const store = useStore();

    const data = computed(() => {
      return store.getters['eventSubscriptions/active'];
    });

    const broadcaster = computed<Broadcaster>(() => {
      return store.getters['broadcaster/data'];
    });

    const twitchEvents = computed(() => {
      return store.getters['twitchEvents/all'];
    });

    const fetchEventSubscriptions = async () => {
      await store.dispatch('twitchEvents/loadAll');
      await store.dispatch('broadcaster/load');
      tauStatusWs.connect();
      twitchEventWs.connect();
    };

    const componentExists = (view: EventSubscription) => {
      const componentName = _.startCase(
        _.camelCase(view.lookup_name.replaceAll('_', '-')),
      ).replace(/ /g, '');
      console.log(componentName);
      const formExists =
        componentName in
        ((resolveComponent('test-form') as ComponentOptions)?.components || {});
      return formExists;
    };

    const tauStatusWs = inject('tauStatusWs') as TauStatusWsService;
    const twitchEventWs = inject('twitchEventWs') as TauTwitchEventWsService;

    onMounted(fetchEventSubscriptions);

    function openTestDialog(view: EventSubscription) {
      view.lookup_name = view.lookup_name.replaceAll('_', '-');
      //.replace('channel-channel', 'channel');

      store.dispatch('UI/setTestFormView', view);
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

    function replayTest(twitchEvent: TwitchEvent) {
      api$.tau.post(
        `twitch-events/${twitchEvent.event_type}/test`,
        twitchEvent.event_data,
      );
    }

    return {
      data,
      broadcaster,
      twitchEvents,
      twitchEventTitle,
      componentExists,
      replay,
      replayTest,
      openTestDialog,
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
</style>
