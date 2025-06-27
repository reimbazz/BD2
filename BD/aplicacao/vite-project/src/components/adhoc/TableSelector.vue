<script setup lang="ts">
import { ref, watch } from 'vue';

interface Props {
  tables: string[];
  selectedTable: string;
}

interface Emits {
  (e: 'update:selectedTable', value: string): void;
}

const props = withDefaults(defineProps<Props>(), {
  tables: () => [],
  selectedTable: ''
});

const emit = defineEmits<Emits>();

const selectedTableLocal = ref(props.selectedTable);

// Observa mudanças locais e emite para o componente pai
watch(selectedTableLocal, (newValue) => {
  emit('update:selectedTable', newValue);
});

// Observa mudanças do componente pai e atualiza localmente
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
        :disabled="tables.length === 0"
        class="mt-2"
        clearable
      >
        <template v-slot:no-data>
          <div class="pa-2">Nenhuma tabela disponível</div>
        </template>
      </v-select>
    </v-card-text>
  </v-card>
</template>
