<script setup lang="ts">
import { ref, watch } from 'vue';

const props = defineProps({
  reportData: {
    type: Array as () => any[],
    default: () => []
  },
  isLoading: {
    type: Boolean,
    default: false
  },
  error: {
    type: String,
    default: ''
  }
});

const headers = ref<any[]>([]);

watch(() => props.reportData, (newData) => {
  if (newData && newData.length > 0) {
    // Extrair cabeçalhos dinamicamente do primeiro item
    headers.value = Object.keys(newData[0]).map(key => ({
      title: key,
      key: key,
      sortable: true
    }));
  } else {
    headers.value = [];
  }
}, { immediate: true });

const downloadCSV = () => {
  if (!props.reportData || props.reportData.length === 0) {
    return;
  }

  // Criar cabeçalho CSV
  const csvHeader = headers.value.map(h => `"${h.title}"`).join(',');
  
  // Criar linhas CSV
  const csvRows = props.reportData.map(row => {
    return headers.value.map(header => {
      // Escapar aspas e envolver em aspas duplas
      const value = row[header.key];
      return `"${String(value).replace(/"/g, '""')}"`;
    }).join(',');
  });
  
  // Combinar cabeçalho e linhas
  const csvContent = [csvHeader, ...csvRows].join('\n');
  
  // Criar blob e link para download
  const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.setAttribute('href', url);
  link.setAttribute('download', `relatorio_adhoc_${new Date().toISOString().split('T')[0]}.csv`);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
};

const exportExcel = () => {
  // Simulação de exportação para Excel (na implementação real usaria uma biblioteca como SheetJS)
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
             :disabled="reportData.length === 0"></v-btn>
      <v-btn icon="mdi-microsoft-excel" variant="text" color="white" @click="exportExcel"
             :disabled="reportData.length === 0"></v-btn>
      <v-btn icon="mdi-printer" variant="text" color="white" @click="printReport"
             :disabled="reportData.length === 0"></v-btn>
    </v-card-title>
    
    <v-card-text>
      <div v-if="isLoading" class="d-flex justify-center align-center" style="min-height: 200px;">
        <v-progress-circular indeterminate color="primary"></v-progress-circular>
      </div>
      
      <div v-else-if="error" class="text-center red--text pa-4">
        <v-icon color="error" class="mr-2">mdi-alert-circle</v-icon>
        {{ error }}
      </div>
      
      <div v-else-if="reportData.length === 0" class="text-center pa-4">
        Configure os critérios do relatório e clique em "Gerar Relatório" para visualizar os resultados.
      </div>
      
      <div v-else>
        <v-data-table
          :headers="headers"
          :items="reportData"
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
