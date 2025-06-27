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
        >
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
                  v-if="!isListOperator(filter.operator) && !isDateType(filter.attribute)"
                  v-model="filter.value"
                  :type="getInputType(filter.attribute)"
                  :label="getPlaceholder(filter.operator)"
                  variant="outlined"
                  density="compact"
                />
                
                <v-text-field
                  v-else-if="isListOperator(filter.operator)"
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
        Selecione uma tabela base para começar a adicionar filtros.
      </v-alert>
    </v-card-text>
  </v-card>
</template>

<script setup lang="ts">
import { computed } from 'vue';

// Interface para os filtros
interface Filter {
  attribute: string;
  operator: string;
  value: any;
  function?: string;
}

// Props
const props = defineProps<{
  modelValue: Filter[];
  availableAttributes: Array<{ 
    name: string; 
    type: string; 
    table?: string; 
    qualified_name?: string;
  }>;
}>();

// Emits
const emit = defineEmits<{
  'update:modelValue': [filters: Filter[]];
}>();

// Computed para formatar os atributos para o v-select
const availableAttributeItems = computed(() => {
  return props.availableAttributes.map(attr => ({
    title: attr.qualified_name || attr.name,
    value: attr.qualified_name || attr.name,
    type: attr.type,
    table: attr.table
  }));
});

// Operadores disponíveis baseados no tipo de dados
const getAvailableOperators = (attribute: string) => {
  const attrInfo = props.availableAttributes.find(
    attr => (attr.qualified_name || attr.name) === attribute
  );
  
  if (!attrInfo) {
    return [
      { title: 'Igual (=)', value: '=' },
      { title: 'Diferente (≠)', value: '!=' }
    ];
  }

  const type = attrInfo.type.toLowerCase();
  
  // Operadores para tipos numéricos
  if (type.includes('int') || type.includes('float') || type.includes('decimal') || type.includes('numeric')) {
    return [
      { title: 'Igual (=)', value: '=' },
      { title: 'Diferente (≠)', value: '!=' },
      { title: 'Maior que (>)', value: '>' },
      { title: 'Menor que (<)', value: '<' },
      { title: 'Maior ou igual (≥)', value: '>=' },
      { title: 'Menor ou igual (≤)', value: '<=' },
      { title: 'Em lista (IN)', value: 'IN' },
      { title: 'Não em lista (NOT IN)', value: 'NOT IN' }
    ];
  }
  
  // Operadores para tipos de texto
  if (type.includes('char') || type.includes('text') || type.includes('varchar')) {
    return [
      { title: 'Igual (=)', value: '=' },
      { title: 'Diferente (≠)', value: '!=' },
      { title: 'Como (LIKE)', value: 'LIKE' },
      { title: 'Como (sem case)', value: 'ILIKE' },
      { title: 'Em lista (IN)', value: 'IN' },
      { title: 'Não em lista (NOT IN)', value: 'NOT IN' }
    ];
  }

  // Operadores para tipos de data
  if (type.includes('date') || type.includes('time')) {
    return [
      { title: 'Igual (=)', value: '=' },
      { title: 'Diferente (≠)', value: '!=' },
      { title: 'Depois de (>)', value: '>' },
      { title: 'Antes de (<)', value: '<' },
      { title: 'A partir de (≥)', value: '>=' },
      { title: 'Até (≤)', value: '<=' }
    ];
  }

  // Operadores padrão
  return [
    { title: 'Igual (=)', value: '=' },
    { title: 'Diferente (≠)', value: '!=' },
    { title: 'Em lista (IN)', value: 'IN' },
    { title: 'Não em lista (NOT IN)', value: 'NOT IN' }
  ];
};

// Funções disponíveis baseadas no tipo de dados
const getAvailableFunctions = (attribute: string) => {
  const attrInfo = props.availableAttributes.find(
    attr => (attr.qualified_name || attr.name) === attribute
  );
  
  if (!attrInfo) return [];

  const type = attrInfo.type.toLowerCase();
  
  // Funções para tipos de texto
  if (type.includes('char') || type.includes('text') || type.includes('varchar')) {
    return [
      { value: 'UPPER', label: 'Maiúsculo (UPPER)' },
      { value: 'LOWER', label: 'Minúsculo (LOWER)' },
      { value: 'LENGTH', label: 'Comprimento (LENGTH)' },
      { value: 'TRIM', label: 'Remover espaços (TRIM)' }
    ];
  }

  // Funções para tipos numéricos
  if (type.includes('int') || type.includes('float') || type.includes('decimal') || type.includes('numeric')) {
    return [
      { value: 'ABS', label: 'Valor absoluto (ABS)' },
      { value: 'ROUND', label: 'Arredondar (ROUND)' },
      { value: 'CEIL', label: 'Teto (CEIL)' },
      { value: 'FLOOR', label: 'Piso (FLOOR)' }
    ];
  }

  // Funções para tipos de data
  if (type.includes('date') || type.includes('time')) {
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

// Computed para formatar as funções para o v-select
const getAvailableFunctionItems = (attribute: string) => {
  return getAvailableFunctions(attribute).map(func => ({
    title: func.label,
    value: func.value
  }));
};

// Verificar se o atributo pode ter função
const canHaveFunction = (attribute: string) => {
  return getAvailableFunctions(attribute).length > 0;
};

// Verificar se é operador de lista
const isListOperator = (operator: string) => {
  return ['IN', 'NOT IN'].includes(operator);
};

// Verificar se é tipo de data
const isDateType = (attribute: string) => {
  const attrInfo = props.availableAttributes.find(
    attr => (attr.qualified_name || attr.name) === attribute
  );
  
  if (!attrInfo) return false;
  
  const type = attrInfo.type.toLowerCase();
  return type.includes('date') || type.includes('time');
};

// Obter tipo de input
const getInputType = (attribute: string) => {
  const attrInfo = props.availableAttributes.find(
    attr => (attr.qualified_name || attr.name) === attribute
  );
  
  if (!attrInfo) return 'text';
  
  const type = attrInfo.type.toLowerCase();
  
  if (type.includes('int') || type.includes('float') || type.includes('decimal') || type.includes('numeric')) {
    return 'number';
  }
  
  if (type.includes('date')) {
    return 'date';
  }
  
  return 'text';
};

// Obter placeholder
const getPlaceholder = (operator: string) => {
  if (operator === 'LIKE' || operator === 'ILIKE') {
    return 'Use % para wildcards (ex: %texto%)';
  }
  
  if (isListOperator(operator)) {
    return 'valor1, valor2, valor3...';
  }
  
  return 'Digite o valor';
};

// Adicionar novo filtro
const addFilter = () => {
  const newFilter: Filter = {
    attribute: '',
    operator: '=',
    value: '',
    function: ''
  };
  
  const newFilters = [...props.modelValue, newFilter];
  emit('update:modelValue', newFilters);
};

// Remover filtro
const removeFilter = (index: number) => {
  const newFilters = props.modelValue.filter((_, i) => i !== index);
  emit('update:modelValue', newFilters);
};

// Quando o atributo muda, resetar operador e valor
const onAttributeChange = (index: number, newValue: string) => {
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
</script>
