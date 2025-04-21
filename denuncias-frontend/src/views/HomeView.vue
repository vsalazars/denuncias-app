<template>
  <v-container>
    <h2>📋 Lista de Denuncias</h2>
    <v-list>
      <v-list-item v-for="denuncia in denuncias" :key="denuncia.id">
        <v-list-item-title>{{ denuncia.descripcion }}</v-list-item-title>
        <v-list-item-subtitle>{{ denuncia.tipo_falta }}</v-list-item-subtitle>
      </v-list-item>
    </v-list>
  </v-container>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/services/axios'

const denuncias = ref([])

const cargarDenuncias = async () => {
  const response = await api.get('denuncias/')
  denuncias.value = response.data
}

onMounted(() => {
  cargarDenuncias()
})
</script>
