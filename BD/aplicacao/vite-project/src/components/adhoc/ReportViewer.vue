<script setup lang="ts">
import { ref, watch, computed } from 'vue';

interface ReportRow {
  [key: string]: any;
}

interface TableHeader {
  title: string;
  key: string;
  sortable: boolean;
}

const props = defineProps<{
  reportData: ReportRow[];
  isLoading: boolean;
  error: string;
}>();

const headers = ref<TableHeader[]>([]);

const hasData = computed(() => props.reportData && props.reportData.length > 0);
const showNoData = computed(() => !props.isLoading && !props.error && !hasData.value);

// Watcher para atualizar cabeçalhos dinamicamente
watch(() => props.reportData, (newData) => {
  if (hasData.value) {
    headers.value = Object.keys(newData[0]).map(key => ({
      title: formatHeaderTitle(key),
      key: key,
      sortable: true
    }));
  } else {
    headers.value = [];
  }
}, { immediate: true });

// Métodos de formatação e exportação
const formatHeaderTitle = (key: string): string => {
  return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
};

const downloadCSV = () => {
  if (!hasData.value) return;

  try {
    const csvHeader = headers.value.map(h => `"${h.title}"`).join(',');
    const csvRows = props.reportData.map(row => {
      return headers.value.map(header => {
        const value = row[header.key];
        return `"${String(value || '').replace(/"/g, '""')}"`;
      }).join(',');
    });
    
    const csvContent = [csvHeader, ...csvRows].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    
    const link = document.createElement('a');
    link.setAttribute('href', url);
    link.setAttribute('download', `relatorio_adhoc_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  } catch (error) {
    console.error('Erro ao baixar CSV:', error);
    alert('Erro ao gerar arquivo CSV');
  }
};

const exportExcel = () => {
  // Placeholder para futura implementação com biblioteca como SheetJS
  alert('Exportação para Excel será implementada na próxima versão.');
};

const printReport = () => {
  window.print();
};
</script>

<template>
  <v-card class="mx-auto">
    <v-card-title class="text-h6 bg-primary text-white">
      <v-icon start>mdi-file-chart</v-icon>
      Relatório ADHOC
      <v-spacer></v-spacer>
      <v-btn icon="mdi-file-download" variant="text" color="white" @click="downloadCSV" 
             :disabled="!hasData"></v-btn>
      <v-btn icon="mdi-microsoft-excel" variant="text" color="white" @click="exportExcel"
             :disabled="!hasData"></v-btn>
      <v-btn icon="mdi-printer" variant="text" color="white" @click="printReport"
             :disabled="!hasData"></v-btn>
    </v-card-title>
    
    <v-card-text>
      <div v-if="isLoading" class="d-flex justify-center align-center" style="min-height: 200px;">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>
      
      <div v-else-if="error" class="text-center red--text pa-4">
        <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
        {{ error }}
      </div>
      
      <div v-else-if="showNoData" class="text-center pa-4">
        Configure os critérios do relatório e clique em "Gerar Relatório" para visualizar os resultados.
      </div>
      
      <div v-else>
        <v-data-table
          :headers="headers"
          :items="props.reportData"
          :items-per-page="10"
          :footer-props="{
            'items-per-page-options': [5, 10, 20, 50, 100],
            'show-first-last-page': true
          }"
          density="comfortable"
          class="elevation-1"
        >
          <template v-slot:no-data>
            <div class="text-center pa-4">Nenhum dado disponível</div>
          </template>
        </v-data-table>
      </div>
    </v-card-text>
  </v-card>
</template>
