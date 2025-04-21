<template>
    <v-container class="fill-height d-flex justify-center align-center">
      <v-card width="400" class="pa-6">
        <v-card-title class="text-h6">🔐 Iniciar Sesión</v-card-title>
        <v-card-text>
          <v-form @submit.prevent="handleLogin">
            <v-text-field
            v-model="correo"
            label="Correo electrónico"
            prepend-icon="mdi-email"
            required
            />
            <v-text-field
              v-model="password"
              label="Contraseña"
              type="password"
              prepend-icon="mdi-lock"
              required
            />
            <v-btn type="submit" color="primary" block>
              Ingresar
            </v-btn>
          </v-form>
        </v-card-text>
      </v-card>
    </v-container>
    <v-alert
  v-if="error"
  type="error"
  dense
  class="mb-4"
  text
>
  {{ error }}
</v-alert>

  </template>
  
  <script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import { jwtDecode } from 'jwt-decode'

const correo = ref('')
const password = ref('')
const error = ref('')
const router = useRouter()

const handleLogin = async () => {
  try {
    const response = await axios.post('http://172.31.64.137:8000/api/token/', {
      correo: correo.value,
      password: password.value,
    })

    const { access, refresh } = response.data
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)

    const decoded = jwtDecode(access)
    console.log('JWT decodificado:', decoded)

    const rol = decoded.rol // 👈 Aquí era 'rol', no 'role'

    // Redirección según el rol
    if (rol === 'ADMIN') {
      router.push('/admin-dashboard')
    } else if (rol === 'OIC') {
      router.push('/oic-dashboard')
    } else if (rol === 'FISCALIA') {
      router.push('/fiscalia-dashboard')
    } else if (rol === 'AUTORIDAD_INVESTIGADORA') {
      router.push('/autoridad-dashboard')
    } else if (rol === 'DENUNCIANTE') {
      router.push('/usuario-dashboard')
    } else {
      router.push('/')
    }

  } catch (err) {
    error.value = 'Credenciales incorrectas'
    console.error('Error de login:', err)
  }
}
</script>
