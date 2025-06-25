<script setup lang="ts">
import { ref, watch, computed } from 'vue';

interface Attribute {
  name: string;
  type: string;
  table?: string;
  qualified_name?: string;
}

interface OrderBy {
  attribute: string;
  direction: 'ASC' | 'DESC';
}

interface AggregateFunction {
  function: string;
  attribute: string;
  alias: string;
}

const emit = defineEmits(['update:orderByColumns']);

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
  },
  orderByColumns: {
    type: Array as () => OrderBy[],
    default: () => []
  }
});

const orderByColumnsLocal = ref<OrderBy[]>(props.orderByColumns);
const newOrderBy = ref<OrderBy>({
  attribute: '',
  direction: 'ASC'
});

const availableAttributes = computed(() => {
  const selectedAttrs = props.attributes.map(attr => attr.qualified_name || attr.name);

  const groupByAttrs = props.groupByAttributes;

  const aggregateAliases = props.aggregateFunctions
    .map(func => func.alias)
    .filter(alias => alias);

  const combinedAttributes = new Set([...selectedAttrs, ...groupByAttrs, ...aggregateAliases]);

  return Array.from(combinedAttributes);
});

watch(() => props.orderByColumns, (newOrdersFromParent) => {
    if (newOrdersFromParent.length > 0 && 'column' in newOrdersFromParent[0]) {
        orderByColumnsLocal.value = newOrdersFromParent.map((order: any) => ({
            attribute: order.column,
            direction: order.direction
        }));
    } else {
        orderByColumnsLocal.value = newOrdersFromParent;
    }
}, {deep: true});

watch (() => props.attributes, (newAvailableAttributes) => {
    if(newOrderBy.value.attribute) {
        const isStillAvailable = newAvailableAttributes.some(
            attr => (attr.qualified_name || attr.name) === newOrderBy.value.attribute
        );

        if(!isStillAvailable) {
            newOrderBy.value.attribute = '';
        }
    }
}, {deep: true});

watch(orderByColumnsLocal, (newValue, oldValue) => {
  const newConvertedValue = newValue.map(order => convertOrderFormat(order));
  
  const oldConvertedValue = oldValue ? oldValue.map(order => convertOrderFormat(order)) : [];

  if (JSON.stringify(newConvertedValue) !== JSON.stringify(oldConvertedValue)) {
    emit('update:orderByColumns', newConvertedValue);
  }
}, { deep: true });

const addOrderBy = () => {
  if (newOrderBy.value.attribute) {
    orderByColumnsLocal.value.push({ ...newOrderBy.value });
    
    // Reset
    newOrderBy.value = {
      attribute: '',
      direction: 'ASC'
    };
  }
};

const removeOrderBy = (index: number) => {
  orderByColumnsLocal.value.splice(index, 1);
};

const moveUp = (index: number) => {
  if (index > 0) {
    const temp = orderByColumnsLocal.value[index];
    orderByColumnsLocal.value[index] = orderByColumnsLocal.value[index - 1];
    orderByColumnsLocal.value[index - 1] = temp;
  }
};

const moveDown = (index: number) => {
  if (index < orderByColumnsLocal.value.length - 1) {
    const temp = orderByColumnsLocal.value[index];
    orderByColumnsLocal.value[index] = orderByColumnsLocal.value[index + 1];
    orderByColumnsLocal.value[index + 1] = temp;
  }
};

// Método auxiliar para converter formatos de ordenação
const convertOrderFormat = (order: OrderBy) => {
  return {
    column: order.attribute,
    direction: order.direction
  };
};
</script>

<template>
  <v-card class="mx-auto mb-4">
    <v-card-title class="text-h6 bg-primary text-white">
      <v-icon start>mdi-sort</v-icon>
      Ordenar Por
    </v-card-title>
    <v-card-text>
      <v-form @submit.prevent="addOrderBy">
        <v-row>
          <v-col cols="12" sm="8">
            <v-select
              v-model="newOrderBy.attribute"
              :items="availableAttributes"
              label="Atributo"
              variant="outlined"
              density="comfortable"
              :disabled="availableAttributes.length === 0"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4">
            <v-select
              v-model="newOrderBy.direction"
              :items="[
                { title: 'Ascendente', value: 'ASC' },
                { title: 'Descendente', value: 'DESC' }
              ]"
              label="Direção"
              variant="outlined"
              density="comfortable"
              item-title="title"
              item-value="value"
            ></v-select>
          </v-col>
        </v-row>
        <v-btn
          color="primary"
          @click="addOrderBy"
          :disabled="!newOrderBy.attribute"
        >
          Adicionar Ordenação
        </v-btn>
      </v-form>

      <v-divider class="my-4"></v-divider>

      <div v-if="orderByColumnsLocal.length > 0">
        <div class="text-subtitle-1 mb-2">Ordem de Classificação</div>
        <v-list density="compact">
          <v-list-item v-for="(order, index) in orderByColumnsLocal" :key="index">
            <v-list-item-title>
              {{ index + 1 }}. {{ order.attribute }} {{ order.direction }}
            </v-list-item-title>
            <template v-slot:append>
              <v-btn icon="mdi-arrow-up" variant="text" density="compact" 
                     @click="moveUp(index)" 
                     :disabled="index === 0"></v-btn>
              <v-btn icon="mdi-arrow-down" variant="text" density="compact" 
                     @click="moveDown(index)" 
                     :disabled="index === orderByColumnsLocal.length - 1"></v-btn>
              <v-btn icon="mdi-delete" variant="text" density="compact" 
                     @click="removeOrderBy(index)"></v-btn>
            </template>
          </v-list-item>
        </v-list>
      </div>
      <div v-else class="text-center pa-2">
        Nenhuma ordenação definida
      </div>
    </v-card-text>
  </v-card>
</template>
