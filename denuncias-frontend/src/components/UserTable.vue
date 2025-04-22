<template>
  <v-card>
    <v-card-title class="text-h6">
      👥 Gestión de Usuarios
      <v-spacer />
      <v-btn color="primary" @click="openDialog = true">➕ Nuevo Usuario</v-btn>
    </v-card-title>

    <v-row class="pa-4" align="center">
  <v-col cols="12" sm="6" md="4">
    <v-select
      v-model="estadoFiltro"
      :items="estados"
      item-title="title"
      item-value="value"
      label="Filtrar por Estado"
      clearable
    />
  </v-col>
</v-row>


    <v-data-table :headers="headers" :items="usuariosFiltrados" class="elevation-1">

      <template #item.correo_enviado="{ item }">
        <v-chip :color="item.correo_enviado ? 'green' : 'red'" text-color="white" small>
          {{ item.correo_enviado ? 'Enviado' : 'No enviado' }}
        </v-chip>
      </template>

      <template #item.estado="{ item }">
        {{ getEstadoTexto(item.estado) }}
      </template>
      <template #item.dependencia_nombre="{ item }">
        {{ item.dependencia?.nombre || '—' }}
      </template>
      <template #item.actions="{ item }">
        <v-btn icon color="blue" @click="editUser(item)">
          <v-icon>mdi-pencil</v-icon>
        </v-btn>
        <v-btn icon color="red" @click="deleteUser(item.id)">
          <v-icon>mdi-delete</v-icon>
        </v-btn>
      </template>
    </v-data-table>

    <!-- Modal nuevo usuario -->
    <v-dialog v-model="openDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h6">Nuevo Usuario</v-card-title>
        <v-card-text>
          <v-text-field v-model="form.first_name" label="Nombre" />
          <v-text-field v-model="form.last_name" label="Apellido" />
          <v-text-field v-model="form.correo" label="Correo electrónico" />

          <v-select
            v-if="form.rol !== 'ADMIN'"
            v-model="form.estado"
            :items="estados"
            item-title="title"
            item-value="value"
            label="Estado"
            required
          />

          <v-select
            v-model="form.rol"
            :items="roles"
            label="Rol"
            required
          />

          <v-select
            v-if="['OIC', 'FISCALIA', 'AUTORIDAD_INVESTIGADORA'].includes(form.rol)"
            v-model="form.dependencia_id"
            :items="dependencias"
            item-title="nombre"
            item-value="id"
            label="Dependencia"
            required
          />
        </v-card-text>
        <v-card-actions>
          <v-btn text @click="resetForm">Cancelar</v-btn>
          <v-btn color="primary" @click="createUser">Guardar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <v-snackbar v-model="snackbar" :color="snackbarColor" timeout="4000" location="bottom right">
      {{ snackbarText }}
    </v-snackbar>
  </v-card>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'

import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL

const snackbar = ref(false)
const snackbarColor = ref('success')
const snackbarText = ref('')

const usuarios = ref([])
const dependencias = ref([])
const openDialog = ref(false)

// 🔍 Filtro por estado
const estadoFiltro = ref('')
const usuariosFiltrados = computed(() => {
  if (!estadoFiltro.value) return usuarios.value
  return usuarios.value.filter(user => user.estado === estadoFiltro.value)
})


const form = ref({
  first_name: '',
  last_name: '',
  correo: '',
  password: '',
  rol: 'DENUNCIANTE',
  estado: '',
  dependencia_id: null
})

const roles = ['ADMIN', 'OIC', 'FISCALIA', 'AUTORIDAD_INVESTIGADORA', 'DENUNCIANTE']

const estados = [
  { value: 'AGS', title: 'Aguascalientes' },
  { value: 'BC', title: 'Baja California' },
  { value: 'BCS', title: 'Baja California Sur' },
  { value: 'CAMP', title: 'Campeche' },
  { value: 'CDMX', title: 'Ciudad de México' },
  { value: 'CHIS', title: 'Chiapas' },
  { value: 'CHIH', title: 'Chihuahua' },
  { value: 'COAH', title: 'Coahuila' },
  { value: 'COL', title: 'Colima' },
  { value: 'DGO', title: 'Durango' },
  { value: 'GTO', title: 'Guanajuato' },
  { value: 'GRO', title: 'Guerrero' },
  { value: 'HGO', title: 'Hidalgo' },
  { value: 'JAL', title: 'Jalisco' },
  { value: 'MEX', title: 'Estado de México' },
  { value: 'MICH', title: 'Michoacán' },
  { value: 'MOR', title: 'Morelos' },
  { value: 'NAY', title: 'Nayarit' },
  { value: 'NL', title: 'Nuevo León' },
  { value: 'OAX', title: 'Oaxaca' },
  { value: 'PUE', title: 'Puebla' },
  { value: 'QRO', title: 'Querétaro' },
  { value: 'QROO', title: 'Quintana Roo' },
  { value: 'SLP', title: 'San Luis Potosí' },
  { value: 'SIN', title: 'Sinaloa' },
  { value: 'SON', title: 'Sonora' },
  { value: 'TAB', title: 'Tabasco' },
  { value: 'TAMPS', title: 'Tamaulipas' },
  { value: 'TLAX', title: 'Tlaxcala' },
  { value: 'VER', title: 'Veracruz' },
  { value: 'YUC', title: 'Yucatán' },
  { value: 'ZAC', title: 'Zacatecas' }
]

const headers = [
  { title: 'Correo', key: 'correo' },
  { title: 'Nombre', key: 'first_name' },
  { title: 'Apellido', key: 'last_name' },
  { title: 'Rol', key: 'rol' },
  { title: 'Estado', key: 'estado' },
  { title: 'Dependencia', key: 'dependencia_nombre' }, // 👈 nuevo campo
  { title: 'Correo Enviado', key: 'correo_enviado' },
  { title: 'Acciones', key: 'actions', sortable: false }
]

const fetchUsuarios = async () => {
  const token = localStorage.getItem('access_token')
  const response = await axios.get(`${API_URL}/api/users/`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  usuarios.value = response.data
}

const cargarDependencias = async (rol, estado) => {
  if (!rol || !estado) return

  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`${API_URL}/api/dependencias/${rol}/?estado=${estado}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    dependencias.value = response.data
  } catch (err) {
    console.error('❌ Error al cargar dependencias:', err)
    dependencias.value = []
  }
}


watch(() => form.value.rol, (rol) => {
  const estado = form.value.estado
  if (['OIC', 'FISCALIA', 'AUTORIDAD_INVESTIGADORA'].includes(rol) && estado) {
    cargarDependencias(rol, estado)
  } else {
    dependencias.value = []
    form.value.dependencia_id = null
  }
})

watch(() => form.value.estado, (estado) => {
  const rol = form.value.rol
  if (['OIC', 'FISCALIA', 'AUTORIDAD_INVESTIGADORA'].includes(rol) && estado) {
    cargarDependencias(rol, estado)
  }
})

const createUser = async () => {
  const token = localStorage.getItem('access_token')
  const userData = { ...form.value }
  delete userData.password

  const isEditing = !!userData.id
  const url = isEditing
    ? `${API_URL}/api/users/${userData.id}/`
    : `${API_URL}/api/users/`

  try {
    const response = await axios[isEditing ? 'put' : 'post'](url, userData, {
      headers: { Authorization: `Bearer ${token}` }
    })

    const enviado = response.data.correo_enviado
    snackbarText.value = enviado
      ? isEditing
        ? '✅ Usuario actualizado correctamente.'
        : '✅ Usuario creado y correo enviado correctamente.'
      : isEditing
        ? '⚠️ Usuario actualizado, pero hubo un detalle con la dependencia.'
        : '⚠️ Usuario creado, pero el correo NO se pudo enviar.'

    snackbarColor.value = enviado ? 'success' : 'warning'
    snackbar.value = true

    openDialog.value = false
    resetForm()
    fetchUsuarios()
  } catch (error) {
    console.error('Error al guardar usuario:', error)
    snackbarText.value = isEditing
      ? '❌ Error al actualizar usuario.'
      : '❌ Error al crear usuario. Verifica que todos los campos estén completos.'
    snackbarColor.value = 'error'
    snackbar.value = true
  }
}


const editUser = async (user) => {
  // Clonamos los campos principales
  form.value = {
    id: user.id,
    first_name: user.first_name,
    last_name: user.last_name,
    correo: user.correo,
    rol: user.rol,
    estado: user.estado,
    dependencia_id: user.dependencia ? user.dependencia.id : user.dependencia_id || null,
    password: ''
  }

  // Si aplica, precarga las dependencias según el rol y estado del usuario
  if (['OIC', 'FISCALIA', 'AUTORIDAD_INVESTIGADORA'].includes(user.rol) && user.estado) {
    await cargarDependencias(user.rol, user.estado)
  } else {
    dependencias.value = []
  }

  openDialog.value = true
}


const deleteUser = async (id) => {
  const token = localStorage.getItem('access_token')
  await axios.delete(`${API_URL}/api/users/${id}/`, {
    headers: { Authorization: `Bearer ${token}` }
  })
  fetchUsuarios()
}

const resetForm = () => {
  form.value = {
    first_name: '',
    last_name: '',
    correo: '',
    rol: 'DENUNCIANTE',
    estado: '',
    dependencia_id: null
  }
  openDialog.value = false
}

const getEstadoTexto = (codigo) => {
  const estado = estados.find(e => e.value === codigo)
  return estado ? estado.title : '-'
}

onMounted(fetchUsuarios)
</script>
