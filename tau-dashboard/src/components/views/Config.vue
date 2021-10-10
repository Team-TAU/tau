<template>
  <h1>TAU Settings</h1>
  <Panel class="dark-header" header="General TAU settings">
    <DataTable :value="settings" stripedRows>
      <Column field="active" header="" headerStyle="width: 6rem;">
        <template #body="{ data }">
          <InputSwitch v-model="data.active" />
        </template>
      </Column>
      <Column
        field="setting"
        header="Setting"
        headerStyle="width: 12rem;"
      ></Column>
      <Column field="description" header="Description"></Column>
    </DataTable>
  </Panel>
  <Panel class="dark-header" header="Twitch EventSub Subscriptions">
    <p>
      Check the subscriptions you would like to use, then click "Update Token"
      at the bottom of the list.
    </p>
    <DataTable :value="eventSubs" stripedRows>
      <Column field="active" header="" headerStyle="width: 6rem;">
        <template #body="{ data }">
          <InputSwitch v-model="data.active" />
        </template>
      </Column>
      <Column
        field="subscription_type"
        header="Setting"
        headerStyle="width: 20rem;"
      ></Column>
      <Column field="description" header="Description"></Column>
    </DataTable>
    <Button @click="updateEventSubs()">Update Subscriptions</Button>
  </Panel>
  <Panel class="dark-header" header="Twitch Helix API Token Scopes">
    <p>
      Check the scopes you would like to use, then click "Update Token" at the
      bottom of the list.
    </p>
    <DataTable :value="scopes" stripedRows>
      <Column field="active" header="" headerStyle="width: 6rem;">
        <template #body="{ data }">
          <InputSwitch v-model="data.required" />
        </template>
      </Column>
      <Column field="scope" header="Scope" headerStyle="width: 20rem;"></Column>
      <Column field="scope" header="Endpoints">
        <template #body="{ data }">
          <template
            v-for="endpoint of scopeEndpoints[data.id]"
            :key="endpoint.id"
          >
            <a :href="endpoint.reference_url" target="_blank">{{
              endpoint.description
            }}</a
            ><br />
          </template>
        </template>
      </Column>
    </DataTable>
  </Panel>
</template>

<script lang="ts">
import {
  EventSubscription,
  EventSubSubscription,
} from '@/models/event-subscription';
import { TwitchHelixEndpoint } from '@/models/twitch-helix-endpoint';
import { TwitchOAuthScope } from '@/models/twitch-oauth-scope';
import eventSub from '@/store/modules/event-subscriptions';
import { computed, defineComponent, onMounted, ref } from 'vue';
import { useStore } from 'vuex';

export default defineComponent({
  name: 'Config',
  setup() {
    const store = useStore();

    const settings = ref([
      {
        active: true,
        setting: 'Use IRC',
        description:
          'Use IRC for grabbing emote data for Channel Point Redemptions',
      },
    ]);

    const eventSubs = computed(function () {
      return store.getters['eventSubscriptions/all'];
    });

    const scopes = computed(function () {
      console.log(store.getters['twitchOAuthScopes/all']);
      return store.getters['twitchOAuthScopes/all'];
    });

    const scopeEndpoints = computed(function () {
      const endpoints = store.getters[
        'twitchHelixEndpoints/all'
      ] as TwitchHelixEndpoint[];
      const scopes = store.getters[
        'twitchOAuthScopes/all'
      ] as TwitchOAuthScope[];
      const endpointsByScope: { [key: string]: TwitchHelixEndpoint[] } = {};

      for (let scope of scopes) {
        endpointsByScope[scope.id] = endpoints.filter(
          (endpoint) => endpoint.scope === scope.id,
        );
      }
      return endpointsByScope;
    });

    async function updateEventSubs() {
      const eventSubscriptions: EventSubscription[] =
        store.getters['eventSubscriptions/all'];
      const payload = eventSubscriptions.map((es) => {
        return {
          id: es.id,
          active: es.active,
        };
      });
      await store.dispatch('eventSubscriptions/bulkActivate', payload);
      window.location.href = 'http://localhost:8008/refresh-token-scope/';
    }

    async function loadHelixData() {
      await store.dispatch('twitchOAuthScopes/loadAll');
      await store.dispatch('twitchHelixEndpoints/loadAll');
    }

    onMounted(loadHelixData);

    return {
      settings,
      eventSubs,
      scopes,
      scopeEndpoints,
      updateEventSubs,
    };
  },
});
</script>
