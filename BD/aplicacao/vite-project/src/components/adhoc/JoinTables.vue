<script setup lang="ts">
import { ref, watch, computed } from "vue";
import type { PropType } from "vue";

interface Join {
  targetTable: string;
  sourceAttribute: string;
  targetAttribute: string;
  joinType: string;
  isTransitive?: boolean;
  intermediateJoins?: Join[];
}

const emit = defineEmits(["update:joins"]);

const props = defineProps({
  tablesFiltersJoin: {
    type: Object as () => { direct: string[], transitive: Record<string, any[]> },
    default: () => ({ direct: [], transitive: {} }),
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

// Computed para criar lista de tabelas disponíveis para o select com indicação do tipo
const availableTables = computed(() => {
  const direct = props.tablesFiltersJoin.direct || [];
  const transitive = Object.keys(props.tablesFiltersJoin.transitive || {});
  
  const directItems = direct.map(table => ({
    title: `${table} (Relação Direta)`,
    value: table,
    props: {
      subtitle: 'Join direto'
    }
  }));
  
  const transitiveItems = transitive.map(table => ({
    title: `${table} (Relação Transitiva)`,
    value: table,
    props: {
      subtitle: 'Join através de tabela intermediária'
    }
  }));
  
  return [...directItems, ...transitiveItems];
});

// Variável para controlar se o join atual é transitivo
const isTransitiveJoin = ref(false);
const transitiveInfo = ref<any>(null);

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
    if (isTransitiveJoin.value && transitiveInfo.value) {
      // Para joins transitivos, adicionar os joins intermediários primeiro
      const sourceTableForJoin = transitiveInfo.value.source_table || props.sourceTable;
      
      // Join da tabela fonte para a intermediária
      const sourceToIntermediate: Join = {
        targetTable: transitiveInfo.value.intermediate_table,
        sourceAttribute: `${sourceTableForJoin}.${transitiveInfo.value.source_to_intermediate.source_column}`,
        targetAttribute: `${transitiveInfo.value.intermediate_table}.${transitiveInfo.value.source_to_intermediate.target_column}`,
        joinType: newJoin.value.joinType,
      };
      
      // Join da tabela intermediária para a alvo
      const intermediateToTarget: Join = {
        targetTable: newJoin.value.targetTable,
        sourceAttribute: `${transitiveInfo.value.intermediate_table}.${transitiveInfo.value.intermediate_to_target.source_column}`,
        targetAttribute: `${newJoin.value.targetTable}.${transitiveInfo.value.intermediate_to_target.target_column}`,
        joinType: newJoin.value.joinType,
      };
      
      joins.value.push(sourceToIntermediate);
      joins.value.push(intermediateToTarget);
    } else {
      // Join direto
      joins.value.push({ ...newJoin.value });
    }
    
    // Reset form
    newJoin.value = {
      targetTable: "",
      sourceAttribute: "",
      targetAttribute: "",
      joinType: "INNER JOIN",
    };
    isTransitiveJoin.value = false;
    transitiveInfo.value = null;
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
      // Verificar se é uma relação direta considerando também tabelas já joinadas
      const isDirect = props.tablesFiltersJoin.direct?.includes(newTable);
      
      // Verificar se alguma tabela já joinada tem relação direta com a nova tabela
      const sourceTablesFromJoins = props.joins?.map(join => join.targetTable) || [];
      
      let hasDirectRelationFromAnySource = isDirect;
      
      // Se não é relação direta da tabela principal, verificar se é de alguma tabela joinada
      if (!isDirect) {
        for (const sourceTable of sourceTablesFromJoins) {
          try {
            const response = await fetch(
              `http://localhost:8000/api/db/tables/${sourceTable}/foreign-keys/${newTable}`
            );
            if (response.ok) {
              const data = await response.json();
              if (data.relations && data.relations.length > 0) {
                hasDirectRelationFromAnySource = true;
                break;
              }
            }
          } catch (error) {
            console.error(`Erro ao verificar relação entre ${sourceTable} e ${newTable}:`, error);
          }
        }
      }
      
      isTransitiveJoin.value = !hasDirectRelationFromAnySource;
      
      if (hasDirectRelationFromAnySource) {
        // Relação direta - buscar atributos normalmente
        const attrs = await props.fetchTargetAttributes(newTable);
        targetAttributes.value = attrs.map(
          (attr: { name: string; type: string }) => ({
            ...attr,
            qualified_name: `${newTable}.${attr.name}`,
          })
        );
        await fetchJoinSuggestions(newTable);
      } else {
        // Relação transitiva - usar as informações pré-calculadas
        const transitiveData = props.tablesFiltersJoin.transitive?.[newTable];
        if (transitiveData && transitiveData.length > 0) {
          transitiveInfo.value = transitiveData[0]; // Usar a primeira opção de caminho transitivo
          
          // Buscar atributos da tabela alvo
          const attrs = await props.fetchTargetAttributes(newTable);
          targetAttributes.value = attrs.map(
            (attr: { name: string; type: string }) => ({
              ...attr,
              qualified_name: `${newTable}.${attr.name}`,
            })
          );
          
          // Para joins transitivos, definir automaticamente os atributos baseados na relação
          const sourceTable = transitiveInfo.value.source_table || props.sourceTable;
          newJoin.value.sourceAttribute = `${sourceTable}.${transitiveInfo.value.source_to_intermediate.source_column}`;
          newJoin.value.targetAttribute = `${newTable}.${transitiveInfo.value.intermediate_to_target.target_column}`;
        }
      }
    } else {
      targetAttributes.value = [];
      suggestedJoinColumns.value = [];
      isTransitiveJoin.value = false;
      transitiveInfo.value = null;
    }
  }
);

const fetchJoinSuggestions = async (targetTable: string) => {
  // Para joins diretos, tentar encontrar a relação FK mais adequada
  // Considerar não apenas a tabela principal, mas também tabelas já joinadas
  
  const sourceTablesFromJoins = props.joins?.map(join => join.targetTable) || [];
  const allSourceTables = [props.sourceTable, ...sourceTablesFromJoins].filter(Boolean);
  
  for (const sourceTable of allSourceTables) {
    try {
      const response = await fetch(
        `http://localhost:8000/api/db/tables/${sourceTable}/foreign-keys/${targetTable}`
      );
      if (response.ok) {
        const data = await response.json();
        if (data.relations && data.relations.length > 0) {
          suggestedJoinColumns.value = data.relations.map((rel: any) => ({
            source: rel.source_column,
            target: rel.target_column,
          }));
          
          // Se há uma sugestão, aplicar automaticamente
          if (suggestedJoinColumns.value.length > 0) {
            const suggestion = suggestedJoinColumns.value[0];
            // Qualificar o atributo de origem com o nome da tabela
            newJoin.value.sourceAttribute = `${sourceTable}.${suggestion.source}`;
            // Qualificar o atributo de destino com o nome da tabela
            newJoin.value.targetAttribute = `${targetTable}.${suggestion.target}`;
            break; // Usar a primeira relação encontrada
          }
        }
      }
    } catch (error) {
      console.error(`Erro ao buscar sugestões de join entre ${sourceTable} e ${targetTable}:`, error);
    }
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
              :items="availableTables"
              item-title="title"
              item-value="value"
              density="comfortable"
              :disabled="!sourceTable"
            >
              <template v-slot:item="{ props, item }">
                <v-list-item
                  v-bind="props"
                  :title="item.raw.title"
                  :subtitle="item.raw.props.subtitle"
                >
                  <template v-slot:prepend>
                    <v-icon 
                      :color="item.raw.props.subtitle === 'Join direto' ? 'success' : 'warning'"
                    >
                      {{ item.raw.props.subtitle === 'Join direto' ? 'mdi-link' : 'mdi-link-variant' }}
                    </v-icon>
                  </template>
                </v-list-item>
              </template>
            </v-select>
          </v-col>
        </v-row>
        
        <v-row>
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
        
        <!-- Informação sobre join transitivo -->
        <v-row v-if="isTransitiveJoin && transitiveInfo">
          <v-col cols="12">
            <v-alert
              type="info"
              variant="tonal"
              density="compact"
              class="mb-2"
            >
              <v-icon start>mdi-information</v-icon>
              <strong>Join Transitivo Detectado</strong>
              <br>
              Esta tabela não tem relacionamento direto com a tabela origem. 
              O sistema criará automaticamente os joins intermediários necessários:
              <br>
              <code>{{ transitiveInfo?.source_table || sourceTable }}</code> → 
              <code>{{ transitiveInfo.intermediate_table }}</code> → 
              <code>{{ newJoin.targetTable }}</code>
            </v-alert>
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
