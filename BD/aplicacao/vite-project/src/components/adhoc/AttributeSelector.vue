<script setup lang="ts">
import { ref, watch, computed } from 'vue';
import { AttributeUtils } from '../../utils';
import type { Attribute } from '../../types';

interface Props {
  attributes: Attribute[];
  selectedAttributes: string[];
}

interface Emits {
  (e: 'update:selectedAttributes', value: string[]): void;
}

const props = withDefaults(defineProps<Props>(), {
  attributes: () => [],
  selectedAttributes: () => []
});

const emit = defineEmits<Emits>();

const selectedAttributesLocal = ref<string[]>([]);

// Inicializar com os valores das props
selectedAttributesLocal.value = [...props.selectedAttributes];

// Observa mudanças locais e emite para o componente pai
watch(selectedAttributesLocal, (newValue) => {
  emit('update:selectedAttributes', newValue);
}, { deep: true });

// Observa mudanças do componente pai e atualiza localmente (sem immediate para evitar loop)
watch(() => props.selectedAttributes, (newValue) => {
  // Só atualiza se realmente mudou para evitar loop infinito
  if (JSON.stringify(newValue) !== JSON.stringify(selectedAttributesLocal.value)) {
    selectedAttributesLocal.value = [...newValue];
  }
});

// Computed para verificar se há atributos selecionados
const hasSelectedAttributes = computed(() => selectedAttributesLocal.value.length > 0);

// Computed para verificar se há atributos disponíveis
const hasAvailableAttributes = computed(() => props.attributes.length > 0);

/**
 * Seleciona todos os atributos disponíveis
 */
const selectAll = (): void => {
  selectedAttributesLocal.value = props.attributes.map(attr => 
    AttributeUtils.getQualifiedName(attr)
  );
};

/**
 * Limpa todas as seleções
 */
const clearSelection = (): void => {
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
          :disabled="!hasAvailableAttributes"
        >
          Selecionar Todos
        </v-btn>
        <v-btn
          variant="text"
          density="compact"
          @click="clearSelection"
          :disabled="!hasSelectedAttributes"
        >
          Limpar Seleção
        </v-btn>
      </div>      
      
      <v-list density="compact" v-if="hasAvailableAttributes">
        <v-list-item v-for="(attr, index) in attributes" :key="index">
          <template v-slot:prepend>
            <v-checkbox
              v-model="selectedAttributesLocal"
              :value="AttributeUtils.getQualifiedName(attr)"
              color="primary"
              hide-details
            ></v-checkbox>
          </template>
          <v-list-item-title>
            {{ AttributeUtils.getQualifiedName(attr) }}
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
