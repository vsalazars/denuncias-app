<!-- src/views/UserManager.vue -->
<template>
    <v-container>
      <h2 class="text-h5 mb-4">👥 Gestión de Usuarios</h2>
  
      <v-btn color="primary" @click="openDialog">➕ Nuevo Usuario</v-btn>
  
      <v-data-table :headers="headers" :items="usuarios" class="mt-4" />
  
      <v-dialog v-model="dialog" persistent max-width="500px">
        <v-card>
          <v-card-title>Registrar Nuevo Usuario</v-card-title>
          <v-card-text>
            <v-text-field v-model="nuevo.correo" label="Correo" required />
            <v-text-field v-model="nuevo.first_name" label="Nombre" />
            <v-text-field v-model="nuevo.last_name" label="Apellido" />
            <v-select v-model="nuevo.rol" :items="roles" label="Rol" required />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="dialog = false">Cancelar</v-btn>
            <v-btn color="primary" @click="registrarUsuario">Registrar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-container>
  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'
  
  const dialog = ref(false)
  const usuarios = ref([])
  const nuevo = ref({ correo: '', first_name: '', last_name: '', rol: '' })
  
  const headers = [
    { text: 'Correo', value: 'correo' },
    { text: 'Nombre', value: 'first_name' },
    { text: 'Apellido', value: 'last_name' },
    { text: 'Rol', value: 'rol' },
  ]
  
  const roles = ['ADMIN', 'OIC', 'FISCALIA', 'AUTORIDAD_INVESTIGADORA', 'DENUNCIANTE']
  
  const openDialog = () => {
    nuevo.value = { correo: '', first_name: '', last_name: '', rol: '' }
    dialog.value = true
  }
  
  const registrarUsuario = async () => {
    try {
      await axios.post('http://localhost:8000/api/usuarios/', nuevo.value)
      dialog.value = false
      await cargarUsuarios()
    } catch (err) {
      console.error('Error al registrar usuario', err)
    }
  }
  
  const cargarUsuarios = async () => {
    try {
      const res = await axios.get('http://localhost:8000/api/usuarios/')
      usuarios.value = res.data
    } catch (err) {
      console.error('Error al cargar usuarios', err)
    }
  }
  
  onMounted(cargarUsuarios)
  </script>
  