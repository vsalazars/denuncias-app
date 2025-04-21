<!-- src/layouts/DashboardLayout.vue -->
<template>
    <v-app>
      <v-app-bar color="primary" dark>
        <v-app-bar-title>🎛️ Panel de {{ roleReadable }}</v-app-bar-title>
  
        <v-spacer />
  
        <!-- Mostrar nombre + apellido -->
        <div class="mr-4 text-caption font-weight-light">
          {{ nombreCompleto }}
          <br />
          Rol: {{ decoded.rol }}
        </div>
  
        <v-btn @click="logout" icon>
          <v-icon>mdi-logout</v-icon>
        </v-btn>
      </v-app-bar>
  
      <v-main class="pa-4">
        <slot />
      </v-main>
    </v-app>
  </template>
  
  <script setup>
  import { useRouter } from 'vue-router'
  import { jwtDecode } from 'jwt-decode'
  import { computed } from 'vue'
  
  const router = useRouter()
  
  const token = localStorage.getItem('access_token')
  const decoded = token ? jwtDecode(token) : {}

console.log('🔍 Token decodificado en DashboardLayout:', decoded)

  
  const roleMap = {
    ADMIN: 'Administrador',
    OIC: 'Órgano Interno de Control',
    FISCALIA: 'Fiscalía',
    AUTORIDAD_INVESTIGADORA: 'Autoridad Investigadora',
    DENUNCIANTE: 'Denunciante',
  }
  
  const roleReadable = computed(() => roleMap[decoded.rol] || 'Usuario')
  const nombreCompleto = computed(() => `${decoded.first_name || ''} ${decoded.last_name || ''}`)
  
  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    router.push('/')
  }
  </script>
  