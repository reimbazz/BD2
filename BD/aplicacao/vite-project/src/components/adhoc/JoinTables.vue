<script setup lang="ts">
import { ref, watch } from "vue";
import type { PropType } from "vue";

interface Join {
  targetTable: string;
  sourceAttribute: string;
  targetAttribute: string;
  joinType: string;
}

const emit = defineEmits(["update:joins"]);

const props = defineProps({
  tablesFiltersJoin: {
    type: Array as () => string[],
    default: () => [],
  },
  sourceTable: {
    type: String,
    default: "",
  },
  sourceAttributes: {
    type: Array as () => {
      name: string;
      type: string;
      table?: string;
      qualified_name?: string;
    }[],
    default: () => [],
  },
  joins: {
    type: Array as () => Join[],
    default: () => [],
  },
  fetchTargetAttributes: {
    type: Function as PropType<
      (tableName: string) => Promise<{ name: string; type: string }[]>
    >,
    required: true,
  } as any,
});

const joins = ref<Join[]>(props.joins);
const newJoin = ref<Join>({
  targetTable: "",
  sourceAttribute: "",
  targetAttribute: "",
  joinType: "INNER JOIN",
});

const joinTypes = [
  { text: "Inner Join", value: "INNER JOIN" },
  { text: "Left Join", value: "LEFT JOIN" },
  { text: "Right Join", value: "RIGHT JOIN" },
  { text: "Full Join", value: "FULL JOIN" },
];

watch(
  joins,
  (newValue) => {
    emit("update:joins", newValue);
  },
  { deep: true }
);

const addJoin = () => {
  if (
    newJoin.value.targetTable &&
    newJoin.value.sourceAttribute &&
    newJoin.value.targetAttribute
  ) {
    joins.value.push({ ...newJoin.value });
    // Reset form
    newJoin.value = {
      targetTable: "",
      sourceAttribute: "",
      targetAttribute: "",
      joinType: "INNER JOIN",
    };
  }
};

const removeJoin = (index: number) => {
  joins.value.splice(index, 1);
};

const targetAttributes = ref<
  { name: string; type: string; qualified_name?: string }[]
>([]);
const suggestedJoinColumns = ref<{ source: string; target: string }[]>([]);

watch(
  () => newJoin.value.targetTable,
  async (newTable) => {
    if (newTable) {
      // Buscar atributos da tabela alvo
      const attrs = await props.fetchTargetAttributes(newTable); // Qualificar os atributos da tabela alvo
      targetAttributes.value = attrs.map(
        (attr: { name: string; type: string }) => ({
          ...attr,
          qualified_name: `${newTable}.${attr.name}`,
        })
      );
      // Buscar sugestões de join baseadas em FKs
      await fetchJoinSuggestions(newTable);
    } else {
      targetAttributes.value = [];
      suggestedJoinColumns.value = [];
    }
  }
);

const fetchJoinSuggestions = async (targetTable: string) => {
  if (!props.sourceTable || !targetTable) return;

  try {
    const response = await fetch(
      `http://localhost:8000/api/db/tables/${props.sourceTable}/foreign-keys/${targetTable}`
    );
    if (response.ok) {
      const data = await response.json();
      suggestedJoinColumns.value = data.relations.map((rel: any) => ({
        source: rel.source_column,
        target: rel.target_column,
      }));
      // Se há uma sugestão, aplicar automaticamente
      if (suggestedJoinColumns.value.length > 0) {
        const suggestion = suggestedJoinColumns.value[0];
        // Qualificar o atributo de origem com o nome da tabela
        newJoin.value.sourceAttribute = `${props.sourceTable}.${suggestion.source}`;
        // Qualificar o atributo de destino com o nome da tabela
        newJoin.value.targetAttribute = `${targetTable}.${suggestion.target}`;
      }
    }
  } catch (error) {
    console.error("Erro ao buscar sugestões de join:", error);
  }
};
</script>

<template>
  <v-card class="mx-auto mb-4">
    <v-card-title class="text-h6 bg-primary text-white mb-4">
      <v-icon start>mdi-table-merge-cells</v-icon>
      Junção de Tabelas
    </v-card-title>
    <v-card-text>
      <v-form @submit.prevent="addJoin">
        <v-row>
          <v-col cols="12" sm="6">
            <v-select
              v-model="newJoin.joinType"
              :items="joinTypes"
              item-title="text"
              item-value="value"
              label="Tipo de Junção"
              variant="outlined"
              density="comfortable"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6">
            <v-select
              v-model="newJoin.targetTable"
              label="Tabela Alvo"
              variant="outlined"
              :items="tablesFiltersJoin"
              density="comfortable"
              :disabled="!sourceTable"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6">
            <v-select
              v-model="newJoin.sourceAttribute"
              label="Atributo da Tabela Origem"
              variant="outlined"
              density="comfortable"
              :disabled="true"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6">
            <v-select
              v-model="newJoin.targetAttribute"
              label="Atributo da Tabela Alvo"
              variant="outlined"
              density="comfortable"
              :disabled="true"
            ></v-select>
          </v-col>
        </v-row>
        <v-btn
          color="primary"
          class="mt-2"
          @click="addJoin"
          :disabled="
            !newJoin.targetTable ||
            !newJoin.sourceAttribute ||
            !newJoin.targetAttribute
          "
        >
          Adicionar Junção
        </v-btn>
      </v-form>

      <v-divider class="my-4"></v-divider>

      <div v-if="joins.length > 0">
        <div class="text-subtitle-1 mb-2">Junções Definidas</div>
        <v-list density="compact">
          <v-list-item v-for="(join, index) in joins" :key="index">
            <template v-slot:prepend>
              <v-icon>mdi-link-variant</v-icon>
            </template>
            <v-list-item-title>
              {{ join.sourceAttribute }} {{ join.joinType }}
              {{ join.targetAttribute }}
            </v-list-item-title>
            <template v-slot:append>
              <v-btn
                icon="mdi-delete"
                variant="text"
                density="compact"
                @click="removeJoin(index)"
              ></v-btn>
            </template>
          </v-list-item>
        </v-list>
      </div>
      <div v-else class="text-center pa-2">Nenhuma junção definida</div>
    </v-card-text>
  </v-card>
</template>
