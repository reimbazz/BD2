<template>
  <v-card class="mx-auto mb-4">
    <v-card-title class="text-h6 bg-primary text-white">
      <v-icon start>mdi-filter</v-icon>
      Filtros
    </v-card-title>
    <v-card-text>
      <!-- Lista de filtros existentes -->
      <div v-if="modelValue.length > 0" class="filters-list">
        <v-card 
          v-for="(filter, index) in modelValue" 
          :key="index" 
          class="filter-item mb-3"
          variant="outlined"
          :color="isFilterValid(filter) ? 'success' : 'warning'"
          :class="{ 'border-opacity-50': !isFilterValid(filter) }"
        >
          <!-- Seletor de lógica (AND/OR) para filtros após o primeiro -->
          <v-card-text v-if="index > 0" class="py-2">
            <v-row justify="center">
              <v-col cols="auto">
                <v-chip-group
                  :model-value="filter.logic"
                  mandatory
                  @update:model-value="onLogicChange(index, $event)"
                >
                  <v-chip value="AND" color="primary" variant="outlined">E (AND)</v-chip>
                  <v-chip value="OR" color="secondary" variant="outlined">OU (OR)</v-chip>
                </v-chip-group>
              </v-col>
            </v-row>
          </v-card-text>
          
          <v-card-text>
            <v-row align="center" class="filter-row">
              <!-- Seletor de atributo -->
              <v-col cols="12" md="3">
                <v-select
                  v-model="filter.attribute"
                  :items="availableAttributeItems"
                  label="Atributo"
                  variant="outlined"
                  density="compact"
                  @update:model-value="onAttributeChange(index, $event)"
                >
                  <template v-slot:item="{ props: itemProps, item }">
                    <v-list-item v-bind="itemProps">
                      <v-list-item-title>{{ item.title }}</v-list-item-title>
                      <v-list-item-subtitle>{{ item.raw.type }}</v-list-item-subtitle>
                    </v-list-item>
                  </template>
                </v-select>
              </v-col>

              <!-- Seletor de operador -->
              <v-col cols="12" md="2">
                <v-select
                  v-model="filter.operator"
                  :items="getAvailableOperators(filter.attribute)"
                  label="Operador"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <!-- Campo de valor -->
              <v-col cols="12" md="3">
                <v-text-field
                  v-if="!FilterUtils.isListOperator(filter.operator) && !isDateType(filter.attribute)"
                  v-model="filter.value"
                  :type="getInputType(filter.attribute)"
                  :label="getPlaceholder(filter.operator)"
                  variant="outlined"
                  density="compact"
                />
                
                <v-text-field
                  v-else-if="FilterUtils.isListOperator(filter.operator)"
                  v-model="filter.value"
                  label="Valores separados por vírgula"
                  placeholder="valor1, valor2, valor3..."
                  variant="outlined"
                  density="compact"
                />

                <v-text-field
                  v-else-if="isDateType(filter.attribute)"
                  v-model="filter.value"
                  type="date"
                  label="Data"
                  variant="outlined"
                  density="compact"
                />
              </v-col>

              <!-- Função opcional -->
              <v-col cols="12" md="3" v-if="canHaveFunction(filter.attribute)">
                <v-select
                  v-model="filter.function"
                  :items="getAvailableFunctionItems(filter.attribute)"
                  label="Função (opcional)"
                  variant="outlined"
                  density="compact"
                  clearable
                />
              </v-col>

              <!-- Botão de remover -->
              <v-col cols="12" md="1" class="text-right">
                <v-btn
                  @click="removeFilter(index)"
                  color="error"
                  variant="text"
                  icon="mdi-delete"
                  size="small"
                />
              </v-col>
            </v-row>
          </v-card-text>
        </v-card>
      </div>

      <!-- Botão para adicionar novo filtro -->
      <div class="text-center mt-4">
        <v-btn
          @click="addFilter"
          color="primary"
          variant="outlined"
          prepend-icon="mdi-plus"
          :disabled="availableAttributes.length === 0"
        >
          Adicionar Filtro
        </v-btn>
      </div>

      <!-- Informação quando não há atributos -->
      <v-alert
        v-if="availableAttributes.length === 0"
        type="info"
        variant="tonal"
        class="mt-4"
      >
        <template v-slot:prepend>
          <v-icon>mdi-information</v-icon>
        </template>
        Selecione uma tabela base para começar a adicionar filtros.
      </v-alert>

      <!-- Resumo dos filtros aplicados -->
      <v-alert
        v-if="modelValue.length > 0"
        type="success"
        variant="tonal"
        class="mt-4"
      >
        <template v-slot:prepend>
          <v-icon>mdi-check-circle</v-icon>
        </template>
        <strong>{{ modelValue.length }}</strong> filtro(s) aplicado(s)
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { AttributeUtils, FilterUtils } from '../../utils';
import type { Attribute, Filter } from '../../types';

interface Props {
  modelValue: Filter[];
  availableAttributes: Attribute[];
}

interface Emits {
  (e: 'update:modelValue', filters: Filter[]): void;
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: () => [],
  availableAttributes: () => []
});

const emit = defineEmits<Emits>();

// Computed para formatar os atributos para o v-select
const availableAttributeItems = computed(() => {
  return AttributeUtils.mapToSelectItems(props.availableAttributes);
});

/**
 * Obtém operadores disponíveis baseado no tipo de dados do atributo
 */
const getAvailableOperators = (attribute: string) => {
  const attrInfo = props.availableAttributes.find(
    attr => AttributeUtils.getQualifiedName(attr) === attribute
  );
  
  if (!attrInfo) {
    return FilterUtils.getAvailableOperators('');
  }
  
  return FilterUtils.getAvailableOperators(attrInfo.type);
};

/**
 * Obtém funções disponíveis baseado no tipo de dados do atributo
 */
const getAvailableFunctions = (attribute: string) => {
  const attrInfo = props.availableAttributes.find(
    attr => AttributeUtils.getQualifiedName(attr) === attribute
  );
  
  if (!attrInfo) return [];

  const type = attrInfo.type.toLowerCase();
  
  // Funções para tipos de texto
  if (FilterUtils.isTextType(type)) {
    return [
      { value: 'UPPER', label: 'Maiúsculo (UPPER)' },
      { value: 'LOWER', label: 'Minúsculo (LOWER)' },
      { value: 'LENGTH', label: 'Comprimento (LENGTH)' },
      { value: 'TRIM', label: 'Remover espaços (TRIM)' }
    ];
  }

  // Funções para tipos numéricos
  if (FilterUtils.isNumericType(type)) {
    return [
      { value: 'ABS', label: 'Valor absoluto (ABS)' },
      { value: 'ROUND', label: 'Arredondar (ROUND)' },
      { value: 'CEIL', label: 'Teto (CEIL)' },
      { value: 'FLOOR', label: 'Piso (FLOOR)' }
    ];
  }

  // Funções para tipos de data
  if (FilterUtils.isDateType(type)) {
    return [
      { value: 'EXTRACT_YEAR', label: 'Extrair ano' },
      { value: 'EXTRACT_MONTH', label: 'Extrair mês' },
      { value: 'EXTRACT_DAY', label: 'Extrair dia' },
      { value: 'DATE_TRUNC_MONTH', label: 'Truncar para mês' },
      { value: 'DATE_TRUNC_YEAR', label: 'Truncar para ano' }
    ];
  }

  return [];
};

/**
 * Computed para formatar as funções para o v-select
 */
const getAvailableFunctionItems = (attribute: string) => {
  return getAvailableFunctions(attribute).map(func => ({
    title: func.label,
    value: func.value
  }));
};

/**
 * Verifica se o atributo pode ter função
 */
const canHaveFunction = (attribute: string): boolean => {
  return getAvailableFunctions(attribute).length > 0;
};

/**
 * Verifica se é um tipo de data
 */
const isDateType = (attribute: string): boolean => {
  const attrInfo = props.availableAttributes.find(
    attr => AttributeUtils.getQualifiedName(attr) === attribute
  );
  
  if (!attrInfo) return false;
  
  return FilterUtils.isDateType(attrInfo.type);
};

/**
 * Obtém o tipo de input baseado no tipo de dados
 */
const getInputType = (attribute: string): string => {
  const attrInfo = props.availableAttributes.find(
    attr => AttributeUtils.getQualifiedName(attr) === attribute
  );
  
  if (!attrInfo) return 'text';
  
  return FilterUtils.getInputType(attrInfo.type);
};

/**
 * Obtém placeholder apropriado para o operador
 */
const getPlaceholder = (operator: string): string => {
  return FilterUtils.getPlaceholder(operator);
};

/**
 * Adiciona novo filtro
 */
const addFilter = (): void => {
  const newFilter: Filter = {
    attribute: '',
    operator: '=',
    value: '',
    logic: 'AND',
    function: ''
  };
  
  const newFilters = [...props.modelValue, newFilter];
  emit('update:modelValue', newFilters);
};

/**
 * Remove filtro
 */
const removeFilter = (index: number): void => {
  const newFilters = props.modelValue.filter((_, i) => i !== index);
  emit('update:modelValue', newFilters);
};

/**
 * Quando o atributo muda, resetar operador e valor
 */
const onAttributeChange = (index: number, newValue: string): void => {
  const newFilters = [...props.modelValue];
  newFilters[index] = {
    ...newFilters[index],
    attribute: newValue,
    operator: '=',
    value: '',
    function: ''
  };
  emit('update:modelValue', newFilters);
};

/**
 * Quando a lógica muda (AND/OR)
 */
const onLogicChange = (index: number, newLogic: 'AND' | 'OR'): void => {
  const newFilters = [...props.modelValue];
  newFilters[index] = {
    ...newFilters[index],
    logic: newLogic
  };
  emit('update:modelValue', newFilters);
};

/**
 * Verifica se um filtro está válido
 */
const isFilterValid = (filter: Filter): boolean => {
  return !!(filter.attribute && filter.operator && filter.value);
};
</script>
