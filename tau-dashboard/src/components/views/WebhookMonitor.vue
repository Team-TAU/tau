<template>
  <h1>Webhook Monitor</h1>
  <Panel class="dark-header" header="Registered Twitch Webhooks">
    <DataTable :value="webhooks" stripedRows>
      <Column field="type" header="Type"></Column>
      <Column field="status" header="Status"></Column>
      <Column field="transport" header="Local">
        <template #body="{ data }">
          <i
            class="pi"
            :class="
              isLocal(data.transport.callback)
                ? ['pi-check', 'green']
                : ['pi-times', 'red']
            "
          ></i>
        </template>
      </Column>
    </DataTable>
    <Button @click="resetWebhooks('all')" class="mr-2 mt-2">All</Button>
    <Button @click="resetWebhooks('remote')" class="mr-2 mt-2">Remote</Button>
    <Button @click="resetWebhooks('broken')" class="mr-2 mt-2">Broken</Button>
    <!-- <Button @click="updateSettings()">Update Settings</Button> -->
  </Panel>
</template>

<script lang="ts">
import { defineComponent, onMounted, ref } from 'vue';

import api$ from '@/services/tau-apis';
import {
  EventsubSubscriptionResponse,
  EventsubSubscription,
} from '@/models/twitch-helix-endpoint';

export default defineComponent({
  setup() {
    const webhooks = ref<EventsubSubscription[]>([]);
    const publicUrl = ref('');

    onMounted(async () => {
      const publicUrlData = await api$.tau.get('public_url');
      publicUrl.value = publicUrlData.public_url.split('/')[2];
      console.log(publicUrl.value);
      const data = await api$.helix.get<EventsubSubscriptionResponse>(
        'eventsub/subscriptions',
      );
      console.log(data.data);
      webhooks.value = data.data;
    });

    const isLocal = function (url: string) {
      const baseUrl = url.split('/')[2];
      return baseUrl === publicUrl.value;
    };

    const resetWebhooks = async function (resetType: string) {
      const payload = {
        type: resetType,
      };
      const resp = await api$.tau.post('reset-webhooks', payload);
    };

    return {
      webhooks,
      resetWebhooks,
      isLocal,
    };
  },
});
</script>

<style lang="scss" scoped>
.green {
  color: var(--green-400);
}
.red {
  color: var(--pink-600);
}
</style>
