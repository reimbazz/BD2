<script setup lang="ts">
import { ref, watch, computed } from "vue";
import { AttributeUtils, ValidationUtils, FormatUtils } from '../../utils';
import { ApiService } from '../../services/apiService';
import { JOIN_TYPES } from '../../types';
import type { Join, Attribute, TableRelations } from '../../types';

interface Props {
  tablesFiltersJoin: TableRelations;
  sourceTable: string;
  sourceAttributes: Attribute[];
  joins: Join[];
  fetchTargetAttributes: (tableName: string) => Promise<{ name: string; type: string }[]>;
}

interface Emits {
  (e: 'update:joins', joins: Join[]): void;
}

const props = withDefaults(defineProps<Props>(), {
  tablesFiltersJoin: () => ({ direct: [], transitive: {} }),
  sourceTable: '',
  sourceAttributes: () => [],
  joins: () => []
});

const emit = defineEmits<Emits>();

// Estado local
const joins = ref<Join[]>([...props.joins]);
const newJoin = ref<Join>({
  targetTable: "",
  sourceAttribute: "",
  targetAttribute: "",
  joinType: "INNER JOIN",
});

// Estado para joins transitivos
const isTransitiveJoin = ref(false);
const transitiveInfo = ref<any>(null);
const targetAttributes = ref<Attribute[]>([]);
const suggestedJoinColumns = ref<{ source: string; target: string }[]>([]);

// Computed para criar lista de tabelas disponíveis para o select
const availableTables = computed(() => {
  const { direct, transitive } = props.tablesFiltersJoin;
  
  const directItems = direct.map(table => ({
    title: `${table} (Relação Direta)`,
    value: table,
    props: { subtitle: 'Join direto' }
  }));
  
  const transitiveItems = Object.keys(transitive).map(table => ({
    title: `${table} (Relação Transitiva)`,
    value: table,
    props: { subtitle: 'Join através de tabela intermediária' }
  }));
  
  return [...directItems, ...transitiveItems];
});

// Observa mudanças nos joins e emite para o componente pai
watch(joins, (newValue) => {
  emit("update:joins", newValue);
}, { deep: true });

/**
 * Adiciona um novo join
 */
const addJoin = (): void => {
  if (!ValidationUtils.validateJoinConfig(newJoin.value)) {
    return;
  }

  if (isTransitiveJoin.value && transitiveInfo.value) {
    addTransitiveJoin();
  } else {
    addDirectJoin();
  }
  
  resetJoinForm();
};

/**
 * Adiciona join transitivo (com tabela intermediária)
 */
const addTransitiveJoin = (): void => {
  if (!transitiveInfo.value) return;

  const sourceTableForJoin = transitiveInfo.value.source_table || props.sourceTable;
  
  const sourceToIntermediate: Join = {
    targetTable: transitiveInfo.value.intermediate_table,
    sourceAttribute: `${sourceTableForJoin}.${transitiveInfo.value.source_to_intermediate.source_column}`,
    targetAttribute: `${transitiveInfo.value.intermediate_table}.${transitiveInfo.value.source_to_intermediate.target_column}`,
    joinType: newJoin.value.joinType,
  };
  
  const intermediateToTarget: Join = {
    targetTable: newJoin.value.targetTable,
    sourceAttribute: `${transitiveInfo.value.intermediate_table}.${transitiveInfo.value.intermediate_to_target.source_column}`,
    targetAttribute: `${newJoin.value.targetTable}.${transitiveInfo.value.intermediate_to_target.target_column}`,
    joinType: newJoin.value.joinType,
  };
  
  joins.value.push(sourceToIntermediate, intermediateToTarget);
};

/**
 * Adiciona join direto
 */
const addDirectJoin = (): void => {
  joins.value.push({ ...newJoin.value });
};

/**
 * Reset do formulário de join
 */
const resetJoinForm = (): void => {
  newJoin.value = {
    targetTable: "",
    sourceAttribute: "",
    targetAttribute: "",
    joinType: "INNER JOIN",
  };
  isTransitiveJoin.value = false;
  transitiveInfo.value = null;
};

/**
 * Remove um join específico
 */
const removeJoin = (index: number): void => {
  joins.value.splice(index, 1);
};

/**
 * Verifica se uma relação é direta considerando tabelas já joinadas
 */
const checkDirectRelation = async (targetTable: string): Promise<boolean> => {
  const isDirect = props.tablesFiltersJoin.direct?.includes(targetTable);
  
  if (isDirect) return true;
  
  // Verificar se alguma tabela já joinada tem relação direta
  const sourceTablesFromJoins = props.joins?.map(join => join.targetTable) || [];
  
  for (const sourceTable of sourceTablesFromJoins) {
    try {
      const relations = await ApiService.getForeignKeyRelations(sourceTable, targetTable);
      if (relations.length > 0) {
        return true;
      }
    } catch (error) {
      console.error(`Erro ao verificar relação entre ${sourceTable} e ${targetTable}:`, error);
    }
  }
  
  return false;
};

/**
 * Busca sugestões de join baseadas em chaves estrangeiras
 */
const fetchJoinSuggestions = async (targetTable: string): Promise<void> => {
  const sourceTablesFromJoins = props.joins?.map(join => join.targetTable) || [];
  const allSourceTables = [props.sourceTable, ...sourceTablesFromJoins].filter(Boolean);
  
  for (const sourceTable of allSourceTables) {
    try {
      const relations = await ApiService.getForeignKeyRelations(sourceTable, targetTable);
      
      if (relations.length > 0) {
        suggestedJoinColumns.value = relations.map(rel => ({
          source: rel.source_column,
          target: rel.target_column,
        }));
        
        // Aplicar primeira sugestão automaticamente
        const suggestion = suggestedJoinColumns.value[0];
        newJoin.value.sourceAttribute = `${sourceTable}.${suggestion.source}`;
        newJoin.value.targetAttribute = `${targetTable}.${suggestion.target}`;
        break;
      }
    } catch (error) {
      console.error(`Erro ao buscar sugestões de join entre ${sourceTable} e ${targetTable}:`, error);
    }
  }
};

// Observa mudanças na tabela alvo selecionada
watch(() => newJoin.value.targetTable, async (newTable) => {
  if (!newTable) {
    targetAttributes.value = [];
    suggestedJoinColumns.value = [];
    isTransitiveJoin.value = false;
    transitiveInfo.value = null;
    return;
  }

  const hasDirectRelation = await checkDirectRelation(newTable);
  isTransitiveJoin.value = !hasDirectRelation;
  
  // Buscar atributos da tabela alvo
  try {
    const attrs = await props.fetchTargetAttributes(newTable);
    targetAttributes.value = AttributeUtils.addTableQualification(attrs, newTable);
  } catch (error) {
    console.error(`Erro ao carregar atributos da tabela ${newTable}:`, error);
    targetAttributes.value = [];
  }
  
  if (hasDirectRelation) {
    await fetchJoinSuggestions(newTable);
  } else {
    // Configurar join transitivo
    const transitiveData = props.tablesFiltersJoin.transitive?.[newTable];
    if (transitiveData && transitiveData.length > 0) {
      transitiveInfo.value = transitiveData[0];
      
      const sourceTable = transitiveInfo.value.source_table || props.sourceTable;
      newJoin.value.sourceAttribute = `${sourceTable}.${transitiveInfo.value.source_to_intermediate.source_column}`;
      newJoin.value.targetAttribute = `${newTable}.${transitiveInfo.value.intermediate_to_target.target_column}`;
    }
  }
});
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
              :items="JOIN_TYPES"
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
          :disabled="!ValidationUtils.validateJoinConfig(newJoin)"
        >
          <v-icon start>mdi-plus</v-icon>
          Adicionar Junção
        </v-btn>
      </v-form>

      <v-divider class="my-4"></v-divider>

      <div v-if="joins.length > 0">
        <div class="text-subtitle-1 mb-2">Junções Definidas</div>
        <v-list density="compact">
          <v-list-item v-for="(join, index) in joins" :key="index">
            <template v-slot:prepend>
              <v-icon color="primary">mdi-link-variant</v-icon>
            </template>
            <v-list-item-title>
              {{ FormatUtils.formatJoin(join) }}
            </v-list-item-title>
            <template v-slot:append>
              <v-btn
                icon="mdi-delete"
                variant="text"
                density="compact"
                color="error"
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
