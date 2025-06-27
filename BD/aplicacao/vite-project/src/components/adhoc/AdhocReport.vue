<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import { ApiService } from '../../services/apiService';
import { AttributeUtils, ValidationUtils } from '../../utils';
import type { Attribute, Join, AggregateFunction, OrderBy as OrderByType, Filter, ReportRequest, TableRelations } from '../../types';

import TableSelector from "./TableSelector.vue";
import AttributeSelector from "./AttributeSelector.vue";
import JoinTables from "./JoinTables.vue";
import GroupBy from "./GroupBy.vue";
import OrderBy from "./OrderBy.vue";
import Filters from "./Filters.vue";
import ReportViewer from "./ReportViewer.vue";

// Estado da aplicação
const tables = ref<string[]>([]);
const tablesJoin = ref<TableRelations>({ direct: [], transitive: {} });
const selectedTable = ref<string>("");
const attributes = ref<Attribute[]>([]);
const selectedAttributes = ref<string[]>([]);
const joins = ref<Join[]>([]);
const groupByAttributes = ref<string[]>([]);
const aggregateFunctions = ref<AggregateFunction[]>([]);
const orderByColumns = ref<OrderByType[]>([]);
const filters = ref<Filter[]>([]);
const reportData = ref<any[]>([]);
const isLoading = ref<boolean>(false);
const error = ref<string>("");
const sqlQuery = ref<string>("");
const showSql = ref<boolean>(false);

/**
 * Carrega tabelas do backend quando o componente for montado
 */
onMounted(async () => {
  try {
    isLoading.value = true;
    tables.value = await ApiService.getTables();
  } catch (err) {
    console.error("Erro ao carregar tabelas:", err);
    error.value = err instanceof Error ? err.message : "Erro ao carregar tabelas. Tente novamente mais tarde.";
  } finally {
    isLoading.value = false;
  }
});

/**
 * Busca atributos de uma tabela específica
 */
const fetchTableAttributes = async (tableName: string): Promise<{ name: string; type: string }[]> => {
  try {
    const columns = await ApiService.getTableColumns(tableName);
    return columns.map(col => ({ name: col.name, type: col.type }));
  } catch (err) {
    console.error(`Erro ao carregar atributos de ${tableName}:`, err);
    return [];
  }
};

/**
 * Carrega atributos das tabelas joinadas
 */
const loadJoinedTablesAttributes = async (): Promise<void> => {
  if (!selectedTable.value) return;

  try {
    isLoading.value = true;
    
    if (joins.value.length === 0) {
      // Se não há joins, carregar apenas os atributos da tabela principal
      const columns = await ApiService.getTableColumns(selectedTable.value);
      attributes.value = columns.map(col => ({
        ...col,
        table: selectedTable.value,
        qualified_name: `${selectedTable.value}.${col.name}`
      }));
    } else {
      // Se há joins, carregar atributos de todas as tabelas envolvidas
      attributes.value = await ApiService.getJoinedTablesColumns(selectedTable.value, joins.value);
    }
    
    // Limpar seleções de atributos que não existem mais
    selectedAttributes.value = selectedAttributes.value.filter(attr => 
      attributes.value.some(availableAttr => 
        availableAttr.qualified_name === attr || availableAttr.name === attr
      )
    );
  } catch (err) {
    console.error("Erro ao carregar atributos das tabelas joinadas:", err);
    error.value = err instanceof Error ? err.message : "Erro ao carregar atributos. Tente novamente mais tarde.";
  } finally {
    isLoading.value = false;
  }
};

/**
 * Carrega atributos quando uma tabela for selecionada
 */
const loadAttributes = async (): Promise<void> => {
  if (!selectedTable.value) return;

  try {
    isLoading.value = true;
    selectedAttributes.value = [];
    
    const columns = await ApiService.getTableColumns(selectedTable.value);
    attributes.value = AttributeUtils.addTableQualification(columns, selectedTable.value);
  } catch (err) {
    console.error("Erro ao carregar atributos:", err);
    error.value = err instanceof Error ? err.message : "Erro ao carregar atributos. Tente novamente mais tarde.";
  } finally {
    isLoading.value = false;
  }
};

/**
 * Computed para atributos filtrados baseado na seleção
 */
const filteredAttributes = computed(() => {
  if (!selectedAttributes.value || selectedAttributes.value.length === 0) {
    return [];
  }

  return AttributeUtils.filterAvailableAttributes(attributes.value, selectedAttributes.value);
});

/**
 * Observa mudanças nos atributos filtrados e limpa dependências
 */
watch(filteredAttributes, (newAvailableAttrs) => {
  const availableNames = newAvailableAttrs.map(attr => AttributeUtils.getQualifiedName(attr));

  // Limpar agrupamentos que não estão mais disponíveis
  groupByAttributes.value = groupByAttributes.value.filter(name => availableNames.includes(name));

  // Limpar funções de agregação que não estão mais disponíveis
  aggregateFunctions.value = aggregateFunctions.value.filter(func => availableNames.includes(func.attribute));

  // Limpar ordenações que não estão mais disponíveis
  orderByColumns.value = orderByColumns.value.filter((col: OrderByType) => 
    availableNames.includes(col.attribute)
  );
}, { deep: true });

/**
 * Carrega tabelas disponíveis para join
 */
const loadTablesJoin = async (): Promise<void> => {
  if (!selectedTable.value) return;

  try {
    isLoading.value = true;
    
    if (joins.value.length === 0) {
      // Se não há joins, usar o endpoint simples
      const usedTables = [selectedTable.value];
      tablesJoin.value = await ApiService.getTransitiveRelations(selectedTable.value, usedTables);
    } else {
      // Se há joins, usar o endpoint que considera joins existentes
      tablesJoin.value = await ApiService.getTransitiveRelationsWithJoins(selectedTable.value, joins.value);
    }
  } catch (err) {
    console.error("Erro ao carregar tabelas para join:", err);
    error.value = err instanceof Error ? err.message : "Erro ao carregar tabelas para join. Tente novamente mais tarde.";
  } finally {
    isLoading.value = false;
  }
};

// Observa mudanças na tabela selecionada
watch(selectedTable, async (newTable) => {
  if (newTable) {
    // Limpar seleções anteriores quando a tabela mudar
    clearDependentSelections();
    await Promise.all([loadAttributes(), loadTablesJoin()]);
  } else {
    clearAllSelections();
  }
});

// Observa mudanças nos joins para atualizar atributos disponíveis
watch(joins, async () => {
  if (selectedTable.value) {
    await Promise.all([loadJoinedTablesAttributes(), loadTablesJoin()]);
  }
}, { deep: true });

/**
 * Limpa seleções dependentes
 */
const clearDependentSelections = (): void => {
  joins.value = [];
  groupByAttributes.value = [];
  aggregateFunctions.value = [];
  orderByColumns.value = [];
  reportData.value = [];
  error.value = "";
  sqlQuery.value = "";
};

/**
 * Limpa todas as seleções
 */
const clearAllSelections = (): void => {
  attributes.value = [];
  selectedAttributes.value = [];
  clearDependentSelections();
};

/**
 * Gera o relatório
 */
const generateReport = async (): Promise<void> => {
  // Validar configuração
  const validation = ValidationUtils.validateReportConfig({
    selectedTable: selectedTable.value,
    selectedAttributes: selectedAttributes.value
  });

  if (!validation.isValid) {
    error.value = validation.message || "Configuração inválida";
    return;
  }

  try {
    isLoading.value = true;
    error.value = "";

    // Preparar o payload com as configurações do relatório
    const payload: ReportRequest = {
      baseTable: selectedTable.value,
      attributes: selectedAttributes.value,
      joins: joins.value,
      groupByAttributes: groupByAttributes.value,
      aggregateFunctions: aggregateFunctions.value,
      orderByColumns: orderByColumns.value.map(order => ({
        attribute: order.attribute,
        direction: order.direction
      })),
      filters: filters.value,
      limit: 1000
    };
    
    const response = await ApiService.generateReport(payload);
    
    // Atualizar dados e query SQL
    reportData.value = response.data;
    sqlQuery.value = response.sql;
    
    if (reportData.value.length === 0) {
      error.value = "A consulta não retornou resultados.";
    }
  } catch (err) {
    console.error("Erro ao gerar relatório:", err);
    error.value = err instanceof Error ? err.message : "Erro ao gerar relatório.";
  } finally {
    isLoading.value = false;
  }
};

/**
 * Limpa todos os filtros e seleções
 */
const clearAll = (): void => {
  selectedTable.value = "";
  clearAllSelections();
};
</script>

<template>
  <v-container fluid>
    <v-row>
      <v-col cols="12">
        <h1 class="text-h4 mb-4">Gerador de Relatórios ADHOC</h1>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="4">
        <TableSelector :tables="tables" v-model:selectedTable="selectedTable" />
      </v-col>

      <v-col cols="12" md="4">
        <AttributeSelector
          :attributes="attributes"
          v-model:selectedAttributes="selectedAttributes"
        />
      </v-col>

      <v-col cols="12" md="4">
        <JoinTables
          :tablesFiltersJoin="tablesJoin"
          :sourceTable="selectedTable"
          :sourceAttributes="attributes"
          v-model:joins="joins"
          :fetchTargetAttributes="fetchTableAttributes"
        />
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="6">
        <GroupBy
          :attributes="filteredAttributes"
          :allAvailableAttributes="attributes"
          v-model:groupByAttributes="groupByAttributes"
          v-model:aggregateFunctions="aggregateFunctions"
        />
      </v-col>

      <v-col cols="12" md="6">
        <OrderBy
          :attributes="filteredAttributes"
          :groupByAttributes="groupByAttributes"
          :aggregateFunctions="aggregateFunctions"
          v-model:orderByColumns="orderByColumns"
        />
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <Filters
          v-model="filters"
          :availableAttributes="attributes"
        />
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" class="d-flex justify-center my-4">
        <v-btn
          color="primary"
          size="large"
          @click="generateReport"
          :loading="isLoading"
          :disabled="!selectedTable || selectedAttributes.length === 0"
        >
          <v-icon start>mdi-file-chart</v-icon>
          Gerar Relatório
        </v-btn>

        <v-btn color="error" size="large" @click="clearAll" class="ml-4">
          <v-icon start>mdi-refresh</v-icon>
          Limpar Tudo
        </v-btn>

        <v-btn
          color="info"
          size="large"
          @click="showSql = !showSql"
          class="ml-4"
          v-if="sqlQuery"
        >
          <v-icon start>mdi-database</v-icon>
          {{ showSql ? "Ocultar SQL" : "Mostrar SQL" }}
        </v-btn>
      </v-col>
    </v-row>

    <v-row v-if="showSql && sqlQuery">
      <v-col cols="12">
        <v-card>
          <v-card-title class="text-h6 bg-info text-white">
            <v-icon start>mdi-database</v-icon>
            Consulta SQL
          </v-card-title>
          <v-card-text>
            <pre class="pa-2">{{ sqlQuery }}</pre>
          </v-card-text>
        </v-card>
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12">
        <ReportViewer
          :reportData="reportData"
          :isLoading="isLoading"
          :error="error"
        />
      </v-col>
    </v-row>
  </v-container>
</template>
