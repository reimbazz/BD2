<script setup lang="ts">
import { ref, watch } from 'vue';

interface Attribute {
  name: string;
  type: string;
}

interface AggregateFunction {
  name: string;
  attribute: string;
  alias: string;
}

const emit = defineEmits(['update:groupByAttributes', 'update:aggregateFunctions']);

const props = defineProps({
  attributes: {
    type: Array as () => Attribute[],
    default: () => []
  },
  groupByAttributes: {
    type: Array as () => string[],
    default: () => []
  },
  aggregateFunctions: {
    type: Array as () => AggregateFunction[],
    default: () => []
  }
});

const groupByAttributesLocal = ref<string[]>(props.groupByAttributes);
const aggregateFunctionsLocal = ref<AggregateFunction[]>(props.aggregateFunctions);
const newAggregate = ref<AggregateFunction>({
  name: 'COUNT',
  attribute: '',
  alias: ''
});

const aggregateFunctionOptions = [
  'COUNT',
  'SUM',
  'AVG',
  'MIN',
  'MAX'
];

watch(groupByAttributesLocal, (newValue) => {
  emit('update:groupByAttributes', newValue);
});

watch(aggregateFunctionsLocal, (newValue) => {
  // Converter para o formato esperado pelo backend ao emitir
  const convertedAggs = newValue.map(agg => convertAggFormat(agg));
  emit('update:aggregateFunctions', convertedAggs);
}, { deep: true });

const addAggregateFunction = () => {
  if (newAggregate.value.name && newAggregate.value.attribute) {
    // Gerar um alias se não foi especificado
    if (!newAggregate.value.alias) {
      newAggregate.value.alias = `${newAggregate.value.name}_${newAggregate.value.attribute}`;
    }
    
    aggregateFunctionsLocal.value.push({ ...newAggregate.value });
    
    // Reset
    newAggregate.value = {
      name: 'COUNT',
      attribute: '',
      alias: ''
    };
  }
};

const removeAggregateFunction = (index: number) => {
  aggregateFunctionsLocal.value.splice(index, 1);
};

// Método auxiliar para converter formatos de agregação
const convertAggFormat = (agg: AggregateFunction) => {
  return {
    function: agg.name,
    attribute: agg.attribute,
    alias: agg.alias
  };
};
</script>

<template>
  <v-card class="mx-auto mb-4">
    <v-card-title class="text-h6 bg-primary text-white">
      <v-icon start>mdi-group</v-icon>
      Agrupar Por
    </v-card-title>
    <v-card-text>
      <v-select
        v-model="groupByAttributesLocal"
        :items="attributes.map(attr => attr.name)"
        label="Atributos para agrupar"
        variant="outlined"
        density="comfortable"
        multiple
        chips
        :disabled="attributes.length === 0"
      >
        <template v-slot:no-data>
          <div class="pa-2">Selecione uma tabela e atributos primeiro</div>
        </template>
      </v-select>

      <v-divider class="my-4"></v-divider>

      <div class="text-subtitle-1 mb-2">Funções de Agregação</div>

      <v-form @submit.prevent="addAggregateFunction">
        <v-row>
          <v-col cols="12" sm="4">
            <v-select
              v-model="newAggregate.name"
              :items="aggregateFunctionOptions"
              label="Função"
              variant="outlined"
              density="comfortable"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4">
            <v-select
              v-model="newAggregate.attribute"
              :items="attributes.map(attr => attr.name)"
              label="Atributo"
              variant="outlined"
              density="comfortable"
              :disabled="attributes.length === 0"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="newAggregate.alias"
              label="Alias (opcional)"
              variant="outlined"
              density="comfortable"
              placeholder="Nome personalizado"
            ></v-text-field>
          </v-col>
        </v-row>
        <v-btn
          color="primary"
          @click="addAggregateFunction"
          :disabled="!newAggregate.name || !newAggregate.attribute"
        >
          Adicionar Função
        </v-btn>
      </v-form>

      <div v-if="aggregateFunctionsLocal.length > 0" class="mt-4">
        <v-list density="compact">
          <v-list-item v-for="(func, index) in aggregateFunctionsLocal" :key="index">
            <v-list-item-title>
              {{ func.name }}({{ func.attribute }})
              <span v-if="func.alias">AS {{ func.alias }}</span>
            </v-list-item-title>
            <template v-slot:append>
              <v-btn icon="mdi-delete" variant="text" density="compact" @click="removeAggregateFunction(index)"></v-btn>
            </template>
          </v-list-item>
        </v-list>
      </div>
      <div v-else class="text-center pa-2 mt-2">
        Nenhuma função de agregação definida
      </div>
    </v-card-text>
  </v-card>
</template>
