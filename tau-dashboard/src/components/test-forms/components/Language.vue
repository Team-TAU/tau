<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px">{{ label }}</label>
    <div class="col">
      <Dropdown
        v-model="inputValue"
        :options="languages"
        optionLabel="label"
        optionValue="value"
        placeholder="Select a language"
        @change="onChange"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref, PropType, onMounted } from 'vue';

export default defineComponent({
  name: 'LanguageInput',
  emits: ['update:value'],
  props: {
    value: {
      type: String,
      required: true,
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const inputValue = ref<string>();
    const languages = ref([
      { value: 'en', label: 'English' },
      { value: 'id', label: 'Bahasa Indonesia' },
      { value: 'ca', label: 'Català' },
      { value: 'da', label: 'Dansk' },
      { value: 'de', label: 'Deutsch' },
      { value: 'es', label: 'Español' },
      { value: 'fr', label: 'Français' },
      { value: 'it', label: 'Italiano' },
      { value: 'hu', label: 'Magyar' },
      { value: 'nl', label: 'Nederlands' },
      { value: 'no', label: 'Norsk' },
      { value: 'pl', label: 'Polski' },
      { value: 'pt', label: 'Português' },
      { value: 'ro', label: 'Română' },
      { value: 'sk', label: 'Slovenčina' },
      { value: 'fi', label: 'Suomi' },
      { value: 'sv', label: 'Svenska' },
      { value: 'tl', label: 'Tagalog' },
      { value: 'vi', label: 'Tiếng Việt' },
      { value: 'tr', label: 'Türkçe' },
      { value: 'cs', label: 'Čeština' },
      { value: 'el', label: 'Ελληνικά' },
      { value: 'bg', label: 'Български' },
      { value: 'ru', label: 'Русский' },
      { value: 'uk', label: 'Українська' },
      { value: 'ar', label: 'العربية' },
      { value: 'ms', label: 'بهاس ملايو' },
      { value: 'hi', label: 'मानक हिन्दी' },
      { value: 'th', label: 'ภาษาไทย' },
      { value: 'zh', label: '中文' },
      { value: 'ja', label: '日本語' },
      { value: 'zh-hk', label: '粵語' },
      { value: 'ko', label: '한국어' },
      { value: 'asl', label: 'American Sign Language' },
      { value: 'other', label: 'Other' },
    ]);
    function onChange(event: any) {
      updateModel(event.value);
    }

    function updateModel(val: any) {
      emit('update:value', val);
    }

    return {
      onChange,
      inputValue,
      languages,
    };
  },
});
</script>
