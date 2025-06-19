<script setup lang="ts">
import { ref, onMounted, watch } from "vue";
import axios from "axios";
import TableSelector from "./TableSelector.vue";
import AttributeSelector from "./AttributeSelector.vue";
import JoinTables from "./JoinTables.vue";
import GroupBy from "./GroupBy.vue";
import OrderBy from "./OrderBy.vue";
import ReportViewer from "./ReportViewer.vue";

// Estado da aplicação
const tables = ref<string[]>([]);
const tablesJoin = ref<string[]>([]);
const selectedTable = ref<string>("");
const attributes = ref<{ name: string; type: string }[]>([]);
const selectedAttributes = ref<string[]>([]);
const joins = ref<any[]>([]);
const groupByAttributes = ref<string[]>([]);
const aggregateFunctions = ref<any[]>([]);
const orderByColumns = ref<any[]>([]);
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

// Carregar atributos quando uma tabela for selecionada
const loadAttributes = async () => {
  if (!selectedTable.value) return;

  try {
    isLoading.value = true;
    selectedAttributes.value = [];
    attributes.value = [];

    isLoading.value = false;
  } catch (err) {
    console.error("Erro ao carregar atributos:", err);
    error.value = "Erro ao carregar atributos. Tente novamente mais tarde.";
    isLoading.value = false;
  }
};

const loadTablesJoin = async () => {
  try {
    isLoading.value = true;
    // Buscar as tabelas disponíveis para join na API
    const response = await axios.get(
      `http://localhost:8000/api/db/tables/${selectedTable.value}/relations`
    );

    tablesJoin.value = response.data.relations;
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

// Função para gerar o relatório
const generateReport = async () => {
  if (!selectedTable.value || selectedAttributes.value.length === 0) {
    error.value = "Selecione uma tabela e pelo menos um atributo.";
    return;
  }

  try {
    isLoading.value = true;
    error.value = "";

    isLoading.value = false;
  } catch (err) {
    console.error("Erro ao gerar relatório:", err);
    error.value = "Erro ao gerar relatório. Tente novamente mais tarde.";
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
        />
      </v-col>
    </v-row>

    <v-row>
      <v-col cols="12" md="6">
        <GroupBy
          :attributes="attributes"
          v-model:groupByAttributes="groupByAttributes"
          v-model:aggregateFunctions="aggregateFunctions"
        />
      </v-col>

      <v-col cols="12" md="6">
        <OrderBy
          :attributes="attributes"
          :groupByAttributes="groupByAttributes"
          v-model:orderByColumns="orderByColumns"
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
