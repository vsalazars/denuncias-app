<!-- src/components/UserTable.vue -->
<template>
    <v-card>
      <v-card-title class="text-h6">
        👥 Gestión de Usuarios
        <v-spacer />
        <v-btn color="primary" @click="openDialog = true">➕ Nuevo Usuario</v-btn>
      </v-card-title>
  
      <v-data-table :headers="headers" :items="usuarios" class="elevation-1">
  <template #item.correo_enviado="{ item }">
    <v-chip :color="item.correo_enviado ? 'green' : 'red'" text-color="white" small>
      {{ item.correo_enviado ? 'Enviado' : 'No enviado' }}
    </v-chip>
  </template>

  <template #item.estado="{ item }">
  {{ getEstadoTexto(item.estado) }}
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
            />
          </v-card-text>
          <v-card-actions>
            <v-btn text @click="resetForm">Cancelar</v-btn>
            <v-btn color="primary" @click="createUser">Guardar</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </v-card>

<v-snackbar v-model="snackbar" :color="snackbarColor" timeout="4000" location="bottom right">
  {{ snackbarText }}
</v-snackbar>


  </template>
  
  <script setup>
  import { ref, onMounted } from 'vue'
  import axios from 'axios'

const snackbar = ref(false)
const snackbarColor = ref('success')
const snackbarText = ref('')

  
  const usuarios = ref([])
  const openDialog = ref(false)
  const form = ref({
    first_name: '',
    last_name: '',
    correo: '',
    password: '',
    rol: 'DENUNCIANTE'
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
  { title: 'Estado', key: 'estado' },               // 👈 aquí
  { title: 'Correo Enviado', key: 'correo_enviado' }, // ✅ nueva columna
  { title: 'Acciones', key: 'actions', sortable: false }
]

  
  const fetchUsuarios = async () => {
    const token = localStorage.getItem('access_token')
    const response = await axios.get('http://172.31.64.137:8000/api/users/', {
      headers: { Authorization: `Bearer ${token}` }
    })
    usuarios.value = response.data
  }
  
  const createUser = async () => {
  const token = localStorage.getItem('access_token')
  const userData = { ...form.value }
  delete userData.password

  try {
    const response = await axios.post('http://172.31.64.137:8000/api/users/', userData, {
      headers: { Authorization: `Bearer ${token}` }
    })

    const enviado = response.data.correo_enviado
    snackbarText.value = enviado
      ? '✅ Usuario creado y correo enviado correctamente.'
      : '⚠️ Usuario creado, pero el correo NO se pudo enviar.'
    snackbarColor.value = enviado ? 'success' : 'warning'
    snackbar.value = true

    openDialog.value = false
    resetForm()
    fetchUsuarios()
  } catch (error) {
    console.error('Error al crear usuario:', error)
    snackbarText.value = '❌ Error al crear usuario. Verifica que todos los campos estén completos.'
    snackbarColor.value = 'error'
    snackbar.value = true
  }
}

 
  const editUser = (user) => {
    form.value = { ...user, password: '' } // no mostramos la contraseña real
    openDialog.value = true
  }
  
  const deleteUser = async (id) => {
    const token = localStorage.getItem('access_token')
    await axios.delete(`http://172.31.64.137:8000/api/users/${id}/`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    fetchUsuarios()
  }
  
  const resetForm = () => {
    form.value = {
      first_name: '',
      last_name: '',
      correo: '',
      rol: ''
    }
    openDialog.value = false
  }

  const getEstadoTexto = (codigo) => {
  const estado = estados.find(e => e.value === codigo)
  return estado ? estado.title : '-'
}
  
  onMounted(fetchUsuarios)
  </script>
  