<template>
  <h1>TwitchUserName</h1>
  <div class="grid">
    <div class="col-6">
      <Panel class="dark-header" header="Event Subscriptions">
        <DataTable :value="data">
          <Column field="subscription_type" header="Event"></Column>
          <Column
            field="status"
            headerStyle="width: 6rem; text-align: center"
            header="Status"
          >
            <template #body="{ data }">
              <i class="pi pi-check" v-if="data.status === 'CON'"></i>
              <i class="pi pi-times" v-else-if="data.status === 'DIS'"></i>
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
          ></Column>
        </DataTable>
      </Panel>
    </div>
    <div class="col-6">
      <Panel class="dark-header" header="Websocket Stream">
        <Accordion :multiple="true">
          <AccordionTab
            v-for="te in twitchEvents"
            :key="te.id"
            :header="te.event_type"
          >
            <div class="prism-container">
              <Prism language="json">{{ te }}</Prism>
            </div>
          </AccordionTab>
        </Accordion>
      </Panel>
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, computed, onMounted } from 'vue';
import { useStore } from 'vuex';

import Prism from 'vue-prism-component';

export default defineComponent({
  name: 'Dashboard',
  components: { Prism },
  setup() {
    const store = useStore();

    const data = computed(function () {
      return store.getters['eventSubscriptions/all'];
    });

    const twitchEvents = computed(function () {
      return store.getters['twitchEvents/all'];
    });

    const fetchEventSubscriptions = async () => {
      await store.dispatch('eventSubscriptions/loadAll');
      await store.dispatch('twitchEvents/loadAll');
    };

    onMounted(fetchEventSubscriptions);

    return {
      data,
      twitchEvents,
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
  overflow-x: scroll;
}
</style>
