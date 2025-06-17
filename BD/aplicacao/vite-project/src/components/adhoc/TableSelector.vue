<script setup lang="ts">
import { ref, watch } from 'vue';

const emit = defineEmits(['update:selectedTable']);

const props = defineProps({
  tables: {
    type: Array as () => string[],
    default: () => []
  },
  selectedTable: {
    type: String,
    default: ''
  }
});

const selectedTableLocal = ref(props.selectedTable);

watch(selectedTableLocal, (newValue) => {
  emit('update:selectedTable', newValue);
});

watch(() => props.selectedTable, (newValue) => {
  selectedTableLocal.value = newValue;
});
</script>

<template>
  <v-card class="mx-auto mb-4">
    <v-card-title class="text-h6 bg-primary text-white">
      <v-icon start>mdi-table</v-icon>
      Seleção de Tabela
    </v-card-title>
    <v-card-text>
      <v-select
        v-model="selectedTableLocal"
        :items="tables"
        label="Selecione uma tabela"
        variant="outlined"
        density="comfortable"
        item-title="text"
        item-value="value"
        return-object
        :disabled="tables.length === 0"
        class="mt-2"
      >
        <template v-slot:no-data>
          <div class="pa-2">Nenhuma tabela disponível</div>
        </template>
      </v-select>
    </v-card-text>
  </v-card>
</template>
