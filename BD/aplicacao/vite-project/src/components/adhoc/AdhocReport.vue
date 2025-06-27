<script setup lang="ts">
import { ref, onMounted, watch, computed } from "vue";
import axios from "axios";
import TableSelector from "./TableSelector.vue";
import AttributeSelector from "./AttributeSelector.vue";
import JoinTables from "./JoinTables.vue";
import GroupBy from "./GroupBy.vue";
import OrderBy from "./OrderBy.vue";
import Filters from "./Filters.vue";
import ReportViewer from "./ReportViewer.vue";

// Estado da aplicação
const tables = ref<string[]>([]);
const tablesJoin = ref<{ direct: string[], transitive: Record<string, any[]> }>({ direct: [], transitive: {} });
const selectedTable = ref<string>("");
const attributes = ref<{ name: string; type: string; table?: string; qualified_name?: string }[]>([]);
const selectedAttributes = ref<string[]>([]);
const joins = ref<any[]>([]);
const groupByAttributes = ref<string[]>([]);
const aggregateFunctions = ref<any[]>([]);
const orderByColumns = ref<any[]>([]);
const filters = ref<any[]>([]);
const reportData = ref<any[]>([]);
const isLoading = ref<boolean>(false);
const error = ref<string>("");
const sqlQuery = ref<string>("");
const showSql = ref<boolean>(false);

// Carregar tabelas do backend quando o componente for montado
onMounted(async () => {
  try {
    isLoading.value = true;
    // Buscar as tabelas disponíveis na API
    const response = await axios.get("http://localhost:8000/api/db/tables");
    console.log("Tabelas carregadas:", response.data.tables);
    tables.value = response.data.tables;
    isLoading.value = false;
  } catch (err) {
    console.error("Erro ao carregar tabelas:", err);
    error.value = "Erro ao carregar tabelas. Tente novamente mais tarde.";
    isLoading.value = false;
  }
});

const fetchTableAttributes = async (tableName: string): Promise<{ name: string; type: string }[]> => {
  try {
    const response = await axios.get(
      `http://localhost:8000/api/db/tables/${tableName}/columns`
    );
    return response.data.columns;
  } catch (err) {
    console.error(`Erro ao carregar atributos de ${tableName}:`, err);
    return [];
  }
};

// Função para carregar atributos das tabelas joinadas
const loadJoinedTablesAttributes = async () => {
  if (!selectedTable.value) return;

  try {
    isLoading.value = true;
    
    if (joins.value.length === 0) {
      // Se não há joins, carregar apenas os atributos da tabela principal
      const response = await axios.get(
        `http://localhost:8000/api/db/tables/${selectedTable.value}/columns`
      );
      attributes.value = response.data.columns.map((col: any) => ({
        ...col,
        table: selectedTable.value,
        qualified_name: `${selectedTable.value}.${col.name}`
      }));
    } else {
      // Se há joins, carregar atributos de todas as tabelas envolvidas
      const response = await axios.post(
        "http://localhost:8000/api/db/tables/joined-columns",
        {
          baseTable: selectedTable.value,
          joins: joins.value
        }
      );
      attributes.value = response.data.columns;
    }
    
    // Limpar seleções de atributos que não existem mais
    selectedAttributes.value = selectedAttributes.value.filter(attr => 
      attributes.value.some(availableAttr => 
        availableAttr.qualified_name === attr || availableAttr.name === attr
      )
    );
    
    isLoading.value = false;
  } catch (err) {
    console.error("Erro ao carregar atributos das tabelas joinadas:", err);
    error.value = "Erro ao carregar atributos. Tente novamente mais tarde.";
    isLoading.value = false;
  }
};

// Carregar atributos quando uma tabela for selecionada
const loadAttributes = async () => {
  if (!selectedTable.value) return;

  try {
    isLoading.value = true;
    selectedAttributes.value = [];
    attributes.value = [];

    const response = await axios.get(
      `http://localhost:8000/api/db/tables/${selectedTable.value}/columns`
    );
    attributes.value = response.data.columns.map((col: any) => ({
      ...col,
      table: selectedTable.value,
      qualified_name: `${selectedTable.value}.${col.name}`
    }));

    isLoading.value = false;
  } catch (err) {
    console.error("Erro ao carregar atributos:", err);
    error.value = "Erro ao carregar atributos. Tente novamente mais tarde.";
    isLoading.value = false;
  }
};

const filteredAttributes = computed(() => {
    if(!selectedAttributes.value || selectedAttributes.value.length === 0) {
        return [];
    }

    return attributes.value.filter(attr =>
        selectedAttributes.value.includes(attr.qualified_name || attr.name)
    );
});

watch(filteredAttributes, (newAvailableAttrs) =>{
    const availableNames = newAvailableAttrs.map(a => a.qualified_name || a.name);

    groupByAttributes.value = groupByAttributes.value.filter(name => availableNames.includes(name));

    aggregateFunctions.value = aggregateFunctions.value.filter(func => availableNames.includes(func.attribute))

    orderByColumns.value = orderByColumns.value.filter(col => availableNames.includes(col.columns))
}, {deep: true});

const loadTablesJoin = async () => {
  try {
    isLoading.value = true;
    
    if (joins.value.length === 0) {
      // Se não há joins, usar o endpoint simples
      const usedTables = [selectedTable.value];
      const usedTablesParam = usedTables.join(',');
      
      const response = await axios.get(
        `http://localhost:8000/api/db/tables/${selectedTable.value}/transitive-relations?used_tables=${usedTablesParam}`
      );
      tablesJoin.value = response.data.relations;
    } else {
      // Se há joins, usar o endpoint que considera joins existentes
      const response = await axios.post(
        `http://localhost:8000/api/db/tables/${selectedTable.value}/transitive-relations-with-joins`,
        {
          baseTable: selectedTable.value,
          joins: joins.value
        }
      );
      tablesJoin.value = response.data.relations;
    }
    
    isLoading.value = false;
  } catch (err) {
    console.error("Erro ao carregar tabelas para join:", err);
    error.value =
      "Erro ao carregar tabelas para join. Tente novamente mais tarde.";
    isLoading.value = false;
  }
};

// Observar mudanças na tabela selecionada
watch(selectedTable, async (newTable) => {
  if (newTable) {
    // Limpar seleções anteriores quando a tabela mudar
    joins.value = [];
    groupByAttributes.value = [];
    aggregateFunctions.value = [];
    orderByColumns.value = [];
    reportData.value = [];

    await loadAttributes();
    await loadTablesJoin();
  } else {
    attributes.value = [];
    selectedAttributes.value = [];
  }
});

// Observar mudanças nos joins para atualizar atributos disponíveis
watch(joins, async () => {
  if (selectedTable.value) {
    await loadJoinedTablesAttributes();
    await loadTablesJoin(); // Recarregar tabelas disponíveis após mudança nos joins
  }
}, { deep: true });

// Função para gerar o relatório
const generateReport = async () => {
  if (!selectedTable.value || selectedAttributes.value.length === 0) {
    error.value = "Selecione uma tabela e pelo menos um atributo.";
    return;
  }

  try {
    isLoading.value = true;
    error.value = "";
      // Preparar o payload com as configurações do relatório
    const payload = {
      baseTable: selectedTable.value,
      attributes: selectedAttributes.value,
      joins: joins.value,
      groupByAttributes: groupByAttributes.value,
      aggregateFunctions: aggregateFunctions.value,
      orderByColumns: orderByColumns.value,
      filters: filters.value,
      limit: 1000
    };
    
    // Enviar solicitação para o backend
    const response = await axios.post(
      "http://localhost:8000/api/db/report",
      payload
    );
    
    // Atualizar dados e query SQL
    reportData.value = response.data.data;
    sqlQuery.value = response.data.sql;
    
    if (reportData.value.length === 0) {
      error.value = "A consulta não retornou resultados.";
    }
    
    isLoading.value = false;
  } catch (err) {
    console.error("Erro ao gerar relatório:", err);
    let errorMessage = "Erro ao gerar relatório.";
    if (typeof err === "object" && err !== null) {
      const e = err as { response?: { data?: { detail?: string } }, message?: string };
      errorMessage += " " + (e.response?.data?.detail || e.message || "");
    }
    error.value = errorMessage;
    isLoading.value = false;
  }
};

// Limpar todos os filtros e seleções
const clearAll = () => {
  selectedTable.value = "";
  attributes.value = [];
  selectedAttributes.value = [];
  joins.value = [];
  groupByAttributes.value = [];
  aggregateFunctions.value = [];
  orderByColumns.value = [];
  filters.value = [];
  reportData.value = [];
  error.value = "";
  sqlQuery.value = "";
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
