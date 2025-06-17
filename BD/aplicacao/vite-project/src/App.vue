<script setup lang="ts">
import AdhocReport from './components/adhoc/AdhocReport.vue';
</script>

<template>
  <v-app>
    <v-app-bar color="primary" dark app>
      <v-app-bar-title>Sistema de Relatórios ADHOC</v-app-bar-title>
    </v-app-bar>
    
    <v-main>
      <AdhocReport />
    </v-main>
    
    <v-footer app>
      <div class="text-center w-100">
        &copy; {{ new Date().getFullYear() }} - Sistema de Relatórios ADHOC
      </div>
    </v-footer>
  </v-app>
</template>

<style>
/* Estilos globais da aplicação */
body {
  font-family: 'Roboto', sans-serif;
  background-color: #f5f5f5;
}

pre {
  background-color: #f1f1f1;
  padding: 10px;
  border-radius: 4px;
  overflow-x: auto;
}
</style>
