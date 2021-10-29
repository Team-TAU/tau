<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <div class="chat-wrapper">
        <TextArea
          placeholder="Message"
          :autoResize="true"
          rows="1"
          v-model="inputValue"
          @input="debounceUpdateModel()"
        />
        <Button
          icon="pi pi-heart"
          class="p-button-rounded p-button-text"
          @click="toggle"
        />
      </div>
    </div>
  </div>
  <OverlayPanel
    ref="op"
    :showCloseIcon="true"
    id="overlay_panel"
    style="width: 450px; max-height: 400px"
  >
    <div class="emote-container">
      <h4>Streamer Emotes</h4>
      <div class="emote-button-group">
        <button
          class="emote-button"
          @click="appendEmote(emote.name)"
          v-for="emote in emotes.streamer"
          :key="emote.id"
        >
          <img :src="emote.images.url_1x" />
        </button>
      </div>
      <h4>Global Emotes</h4>
      <div class="emote-button-group">
        <button
          class="emote-button"
          @click="appendEmote(emote.name)"
          v-for="emote in emotes.global"
          :key="emote.id"
        >
          <img :src="emote.images.url_1x" />
        </button>
      </div>
    </div>
  </OverlayPanel>
</template>

<script lang="ts">
import { defineComponent, PropType, reactive, ref, onMounted } from 'vue';
import tau from '@/services/tau-apis';
import _ from 'lodash';
import { useStore } from 'vuex';

export interface EmoteResponse {
  data: Emote[];
}

export interface Emote {
  id: string;
  name: string;
  images: {
    url_1x: string;
    url_2x: string;
    url_4x: string;
  };
  tier?: string;
  emote_type?: string;
  emote_set_id?: string;
  format: string[];
  scale: string[];
  theme_mode: string[];
}

export interface EmoteData {
  begin: number;
  end: number;
  id: string;
}

export interface TwitchMessage {
  text: string;
  emotes: EmoteData[];
}

export default defineComponent({
  name: 'EmoteMessage',
  emits: ['update:value'],
  props: {
    value: {
      type: Object as PropType<TwitchMessage>,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const inputValue = ref<string>('');

    const op = ref();
    const store = useStore();
    const emotes = reactive<{ global: Emote[]; streamer: Emote[] }>({
      global: [],
      streamer: [],
    });

    const debounceUpdateModel: any = _.debounce(() => {
      updateModel();
    }, 400);

    const updateModel = () => {
      const text = inputValue.value.trim();
      // text "finite6ThrowBall finite6RoboOllie hello world"
      let emoteMap: { [key: string]: string } = {};
      emoteMap = emotes.streamer.reduce((acc, cur) => {
        acc[cur.name] = cur.id;
        return acc;
      }, emoteMap);
      emoteMap = emotes.global.reduce((acc, cur) => {
        acc[cur.name] = cur.id;
        return acc;
      }, emoteMap);
      const textArr = text.split(' ').reduce((acc: any[], word) => {
        const prev = acc.length === 0 ? null : acc[acc.length - 1];
        const start = !prev ? 0 : prev.start + prev.word.length + 1;
        return [...acc, { start, word }];
      }, []);

      const emoteArray = textArr.reduce((acc: any[], word) => {
        if (word.word in emoteMap) {
          return [
            ...acc,
            {
              begin: word.start,
              end: word.start + word.word.length - 1,
              id: emoteMap[word.word],
            },
          ];
        } else {
          return acc;
        }
      }, []);

      const message: TwitchMessage = {
        text,
        emotes: emoteArray,
      };

      console.log(message);

      emit('update:value', message);
    };

    function toggle(event: any) {
      op.value.toggle(event);
    }

    function appendEmote(name: string) {
      const curVal = inputValue.value;
      if (curVal.length === 0 || curVal[curVal.length - 1] === ' ') {
        inputValue.value = `${inputValue.value}${name} `;
      } else {
        inputValue.value = `${inputValue.value} ${name} `;
      }
      updateModel();
    }

    onMounted(async () => {
      const broadcaster_id = store.getters['broadcaster/data'].id;
      emotes.global = (
        await tau.helix.get<EmoteResponse>(`chat/emotes/global`)
      ).data;
      emotes.streamer = (
        await tau.helix.get<EmoteResponse>(`chat/emotes`, {
          broadcaster_id,
        })
      ).data;
    });

    return {
      emotes,
      appendEmote,
      debounceUpdateModel,
      op,
      toggle,
      inputValue,
    };
  },
});
</script>

<style lang="scss" scoped>
.emote-container {
  max-height: 368px;
  overflow-y: auto;
  .emote-button-group {
    display: flex;
    flex-wrap: wrap;

    .emote-button {
      width: 38px;
      height: 38px;
      margin: 2px;
      border-radius: 5px;
      border: none;
      display: flex;
      align-items: center;
      justify-content: center;
      background: none;
      &:hover {
        background-color: #dddddd;
      }
    }
  }
}

.chat-wrapper {
  position: relative;
  TextArea {
    width: 100%;
    padding-right: 40px;
  }
  Button {
    position: absolute;
    right: 0;
    bottom: 5px;
  }
}

h4 {
  margin: 0;
}
</style>
