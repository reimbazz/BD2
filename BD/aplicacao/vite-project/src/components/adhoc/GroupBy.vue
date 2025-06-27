<script setup lang="ts">
import { computed, ref, watch } from "vue";
import type { Attribute, AggregateFunction } from "../../types";
import { AttributeUtils, AggregateUtils } from "../../utils";

const emit = defineEmits<{
  "update:groupByAttributes": [value: string[]];
  "update:aggregateFunctions": [value: AggregateFunction[]];
}>();

const props = defineProps<{
  attributes: Attribute[];
  allAvailableAttributes: Attribute[];
  groupByAttributes: string[];
  aggregateFunctions: AggregateFunction[];
}>();

const groupByAttributesLocal = ref<string[]>(props.groupByAttributes);
const aggregateFunctionsLocal = ref<AggregateFunction[]>(props.aggregateFunctions);
const newAggregate = ref<AggregateFunction>(AggregateUtils.createDefault());

// Watchers para sincronização bidirecional
watch(groupByAttributesLocal, (newValue) => {
  emit("update:groupByAttributes", newValue);
});

watch(
  aggregateFunctionsLocal,
  (newValue) => {
    emit("update:aggregateFunctions", newValue);
  },
  { deep: true }
);

watch(
  () => props.groupByAttributes,
  (newValue) => {
    groupByAttributesLocal.value = newValue;
  }
);

watch(
  () => props.aggregateFunctions,
  (newValue) => {
    aggregateFunctionsLocal.value = newValue;
  },
  { deep: true }
);

// Auto-selecionar função padrão quando atributo é escolhido
watch(
  () => newAggregate.value.attribute,
  (newAttr) => {
    if (newAttr) {
      newAggregate.value.function = "COUNT";
    }
  }
);

// Funções computadas
const availableFunctions = computed(() => {
  const attr = props.allAvailableAttributes.find(
    a => AttributeUtils.getQualifiedName(a) === newAggregate.value.attribute
  );
  
  if (!attr) return ["COUNT"];
  
  return AggregateUtils.getAvailableFunctions(attr.type);
});

const attributeSelectItems = computed(() => {
  const items = AttributeUtils.mapToSelectItems(props.attributes);
  return items;
});

const allAttributeSelectItems = computed(() => {
  const items = AttributeUtils.mapToSelectItems(props.allAvailableAttributes);
  return items;
});

// Métodos
const addAggregateFunction = () => {
  if (!AggregateUtils.validate(newAggregate.value)) return;

  // Gerar alias se não especificado
  if (!newAggregate.value.alias) {
    newAggregate.value.alias = AggregateUtils.generateAlias(newAggregate.value);
  }

  aggregateFunctionsLocal.value.push({ ...newAggregate.value });
  newAggregate.value = AggregateUtils.createDefault();
};

const removeAggregateFunction = (index: number) => {
  aggregateFunctionsLocal.value.splice(index, 1);
};
</script>

<template>
  <v-card class="mx-auto mb-4">
    <v-card-title class="text-h6 bg-primary text-white">
      <v-icon start>mdi-group</v-icon>
      Agrupar Por
    </v-card-title>
    <v-card-text class="pa-4">
      <!-- Debug: mostrar informações sobre atributos -->
      <v-alert 
        v-if="props.attributes.length === 0" 
        type="info" 
        variant="tonal" 
        class="mb-4"
      >
        Nenhum atributo disponível. Certifique-se de selecionar uma tabela primeiro.
      </v-alert>

      <v-alert 
        v-else 
        type="success" 
        variant="tonal" 
        class="mb-4"
      >
        {{ props.attributes.length }} atributo(s) carregado(s) da tabela.
      </v-alert>

      <v-select
        v-model="groupByAttributesLocal"
        :items="attributeSelectItems"
        item-title="title"
        item-value="value"
        label="Atributos para agrupar"
        variant="outlined"
        density="comfortable"
        multiple
        chips
        :disabled="props.attributes.length === 0"
      >
        <template v-slot:no-data>
          <div class="pa-2">Selecione uma tabela e atributos primeiro</div>
        </template>
        <template v-slot:prepend-item>
          <div class="pa-2 text-caption">
            {{ props.attributes.length }} atributo(s) disponível(eis)
          </div>
        </template>
      </v-select>

      <v-divider class="my-4"></v-divider>

      <div class="text-subtitle-1 mb-2">Funções de Agregação</div>

      <v-form @submit.prevent="addAggregateFunction">
        <v-row>
          <v-col cols="12" sm="4">
            <v-select
              v-model="newAggregate.function"
              :items="availableFunctions"
              label="Função"
              variant="outlined"
              density="comfortable"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="4">
            <v-select
              v-model="newAggregate.attribute"
              :items="allAttributeSelectItems"
              item-title="title"
              item-value="value"
              label="Atributo"
              variant="outlined"
              density="comfortable"
              :disabled="props.attributes.length === 0"
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
          :disabled="!AggregateUtils.validate(newAggregate)"
        >
          Adicionar Função
        </v-btn>
      </v-form>

      <div v-if="aggregateFunctionsLocal.length > 0" class="mt-4">
        <v-list density="compact">
          <v-list-item
            v-for="(func, index) in aggregateFunctionsLocal"
            :key="index"
          >
            <v-list-item-title>
              {{ func.function }}({{ func.attribute }})
              <span v-if="func.alias">AS {{ func.alias }}</span>
            </v-list-item-title>
            <template v-slot:append>
              <v-btn
                icon="mdi-delete"
                variant="text"
                density="compact"
                @click="removeAggregateFunction(index)"
              ></v-btn>
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
