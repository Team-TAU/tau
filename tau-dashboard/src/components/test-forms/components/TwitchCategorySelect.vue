<template>
  <div class="field grid">
    <label class="col-fixed" style="width: 140px" for="category">{{
      label
    }}</label>
    <div class="col">
      <AutoComplete
        v-model="category"
        :dropdown="true"
        :suggestions="categories"
        forceSelection
        @complete="searchCategories($event)"
        field="name"
        @item-select="onOptionSelect"
      />
    </div>
  </div>
</template>

<script lang="ts">
import { defineComponent, ref } from 'vue';
import tau from '@/services/tau-apis';

interface TwitchCategory {
  box_art_url: string;
  id: string;
  name: string;
}

export default defineComponent({
  name: 'TwitchCategorySelect',
  emits: ['update:categoryId', 'update:categoryName'],
  props: {
    categoryId: {
      type: String,
      default: '',
    },
    categoryName: {
      type: String,
      default: '',
    },
    label: {
      type: String,
      required: true,
    },
  },
  setup(props, { emit }) {
    const categories = ref<TwitchCategory[]>([]);

    const category = ref<TwitchCategory>();

    function onOptionSelect(event: any) {
      const name = category.value?.name;
      const id = category.value?.id;
      updateModel(name, id);
    }

    function updateModel(name: string | undefined, id: string | undefined) {
      emit('update:categoryId', id);
      emit('update:categoryName', name);
    }

    async function searchCategories(event: any) {
      const cats = await tau.helix.get(
        `search/categories?query=${event.query}`,
      );
      categories.value = cats.data.map((cat: any) => {
        return { id: cat.id, name: cat.name };
      });
    }

    return {
      onOptionSelect,
      searchCategories,
      categories,
      category,
    };
  },
});
</script>
