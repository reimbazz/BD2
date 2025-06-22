<script setup lang="ts">
import { ref, watch } from 'vue';

interface Attribute {
  name: string;
  type: string;
  table?: string;
  qualified_name?: string;
}

const emit = defineEmits(['update:selectedAttributes']);

const props = defineProps({
  attributes: {
    type: Array as () => Attribute[],
    default: () => []
  },
  selectedAttributes: {
    type: Array as () => string[],
    default: () => []
  }
});

const selectedAttributesLocal = ref<string[]>(props.selectedAttributes);

watch(selectedAttributesLocal, (newValue) => {
  emit('update:selectedAttributes', newValue);
});

watch(() => props.selectedAttributes, (newValue) => {
  selectedAttributesLocal.value = newValue;
});

const selectAll = () => {
  selectedAttributesLocal.value = props.attributes.map(attr => 
    attr.qualified_name || attr.name
  );
};

const clearSelection = () => {
  selectedAttributesLocal.value = [];
};
</script>

<template>
  <v-card class="mx-auto mb-4">
    <v-card-title class="text-h6 bg-primary text-white">
      <v-icon start>mdi-format-list-checks</v-icon>
      Seleção de Atributos
    </v-card-title>
    <v-card-text>
      <div class="d-flex justify-space-between mb-2">
        <v-btn
          variant="text"
          density="compact"
          @click="selectAll"
          :disabled="attributes.length === 0"
        >
          Selecionar Todos
        </v-btn>
        <v-btn
          variant="text"
          density="compact"
          @click="clearSelection"
          :disabled="selectedAttributesLocal.length === 0"
        >
          Limpar Seleção
        </v-btn>
      </div>      <v-list density="compact" v-if="attributes.length > 0">
        <v-list-item v-for="(attr, index) in attributes" :key="index">
          <template v-slot:prepend>
            <v-checkbox
              v-model="selectedAttributesLocal"
              :value="attr.qualified_name || attr.name"
              color="primary"
              hide-details
            ></v-checkbox>
          </template>
          <v-list-item-title>
            {{ attr.qualified_name || attr.name }}
          </v-list-item-title>
          <v-list-item-subtitle>
            {{ attr.type }}
            <span v-if="attr.table" class="text-info ml-2">({{ attr.table }})</span>
          </v-list-item-subtitle>
        </v-list-item>
      </v-list>
      <div v-else class="text-center pa-4">
        Selecione uma tabela para ver os atributos disponíveis
      </div>
    </v-card-text>
  </v-card>
</template>
