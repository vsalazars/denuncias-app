<template>
    <DashboardLayout>
      <h1>🎛️ Panel del Órgano Interno de Control</h1>
      <p>Estado asignado: {{ estadoUsuario }}</p>
  
      <v-data-table :headers="headers" :items="denunciasFormateadas" class="elevation-1">
        <template #item.folio="{ item }">
          <a href="#" @click.prevent="mostrarDetalles(item.original)">
            {{ item.folio }}
          </a>
        </template>
  
        <template #item.dias_transcurridos="{ item }">
          <v-chip :color="item.dias_transcurridos > 15 ? 'red' : 'green'" dark small>
            {{ item.dias_transcurridos }} días
            <template v-if="item.dias_transcurridos > 15"> ⚠️</template>
          </v-chip>
        </template>
  
        <template #item.dependencia_turnada="{ item }">
          <span>{{ item.dependencia_turnada || '—' }}</span>
        </template>


        <template #item.faltas_graves="{ item }">
          <v-chip v-for="(f, i) in item.faltas_graves" :key="i" color="red" class="ma-1" size="small">
            {{ f }}
          </v-chip>
        </template>
  
        <template #item.faltas_no_graves="{ item }">
          <v-chip v-for="(f, i) in item.faltas_no_graves" :key="i" color="orange" class="ma-1" size="small">
            {{ f }}
          </v-chip>
        </template>
  
        <template #item.hechos_corrupcion="{ item }">
          <v-chip v-for="(f, i) in item.hechos_corrupcion" :key="i" color="deep-purple" class="ma-1" size="small">
            {{ f }}
          </v-chip>
        </template>
  
        <template #item.acciones="{ item }">
          <v-btn color="green" small class="ma-1" @click="abrirModalConclusion(item)">Concluir con resolución</v-btn>
          <v-btn color="blue" small class="ma-1" @click="abrirModalTurno(item)">Turnar a Autoridad</v-btn>
          <v-btn color="deep-purple" small class="ma-1" @click="turnarFiscalia(item)">Turnar a Fiscalía</v-btn>
          <v-btn color="red" small class="ma-1" @click="rechazarDenuncia(item)">Rechazar</v-btn>
        </template>
      </v-data-table>

      <!-- Detalles Modal -->
<v-dialog v-model="dialog" max-width="800">
  <v-card>
    <v-card-title class="text-h6">📋 Detalles de la Denuncia</v-card-title>
    <v-card-text v-if="denunciaSeleccionada">
      <p><strong>Folio:</strong> {{ denunciaSeleccionada.folio }}</p>
      <p><strong>Descripción:</strong> {{ denunciaSeleccionada.descripcion_hechos }}</p>

      <v-divider class="my-4" />

      <h3 class="text-subtitle-1">📜 Historial de Seguimientos</h3>

      <!-- ✅ Línea del tiempo completa -->
      <v-timeline side="end" dense>
        <v-timeline-item
          v-for="(item, index) in historial"
          :key="index"
          :dot-color="colorEstado(item.estado)"
          size="small"
        >
          <strong>{{ obtenerLabelEstado(item.estado) }}</strong><br />
          <span class="text-caption">{{ new Date(item.fecha_turno).toLocaleString('es-MX') }}</span><br />
          <span v-if="item.comentario && !item.comentario.includes('ID')">📝 {{ item.comentario }}</span><br />
          <span v-if="item.dependencia">🏛️ {{ item.dependencia.nombre }}</span>
        </v-timeline-item>
      </v-timeline>
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn text @click="dialog = false">Cerrar</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>


  
      <!-- Rechazo Modal -->
      <v-dialog v-model="dialogRechazo" max-width="600">
        <v-card>
          <v-card-title class="text-h6">❌ Rechazar Denuncia</v-card-title>
          <v-card-text>
            <p><strong>Folio:</strong> {{ denunciaRechazo?.folio }}</p>
            <v-textarea v-model="comentarioRechazo" label="Motivo del rechazo" rows="4" auto-grow outlined />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="dialogRechazo = false">Cancelar</v-btn>
            <v-btn color="red" @click="confirmarRechazo">Confirmar Rechazo</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
  
      <!-- Conclusión Modal -->
      <v-dialog v-model="dialogConclusion" max-width="600">
        <v-card>
          <v-card-title class="text-h6">✅ Concluir Denuncia</v-card-title>
          <v-card-text>
            <p><strong>Folio:</strong> {{ denunciaConclusion?.folio }}</p>
            <v-textarea v-model="comentarioConclusion" label="Resumen de la resolución" rows="4" auto-grow outlined />
          </v-card-text>
          <v-card-actions>
            <v-spacer />
            <v-btn text @click="dialogConclusion = false">Cancelar</v-btn>
            <v-btn color="green" @click="confirmarConclusion">Confirmar Conclusión</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>

      <v-dialog v-model="dialogTurno" max-width="600">
  <v-card>
    <v-card-title class="text-h6">📤 Turnar a Autoridad Investigadora</v-card-title>
    <v-card-text>
      <p><strong>Folio:</strong> {{ denunciaTurno?.folio }}</p>

      <v-select
        v-model="dependenciaSeleccionada"
        :items="dependenciasInvestigadoras"
        item-title="nombre"
        item-value="id"
        label="Selecciona la autoridad investigadora"
        required
      />

      <v-textarea
        v-model="comentarioTurno"
        label="Comentario del turno"
        rows="3"
        auto-grow
        outlined
        required
      />
    </v-card-text>

    <v-card-actions>
      <v-spacer />
      <v-btn text @click="dialogTurno = false">Cancelar</v-btn>
      <v-btn color="blue" @click="confirmarTurnoAutoridad">Confirmar Turno</v-btn>
    </v-card-actions>
  </v-card>
</v-dialog>


    </DashboardLayout>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import { jwtDecode } from 'jwt-decode'
  import DashboardLayout from '@/layouts/DashboardLayout.vue'
  import mockData from '@/fixtures/mock_denuncias.json'
  import axios from 'axios'
  
  const API_URL = import.meta.env.VITE_API_URL

  const estadoUsuario = ref('')
  const denuncias = ref([])
  const dialog = ref(false)
  const denunciaSeleccionada = ref(null)
  
  const dialogRechazo = ref(false)
  const dialogConclusion = ref(false)
  const denunciaConclusion = ref(null)
  const comentarioConclusion = ref('')
  const denunciaRechazo = ref(null)
  const comentarioRechazo = ref('')


  const dialogTurno = ref(false)
  const denunciaTurno = ref(null)
  const dependenciaSeleccionada = ref(null)
  const dependenciasInvestigadoras = ref([])

  const comentarioTurno = ref('')


  
  // Mapeo de claves (para backend) y etiquetas (para frontend)
  const ESTADOS_VISIBLES = {
  CONCLUIDA_OIC: {
    backend: 'CONCLUIDA_OIC',
    label: 'Concluida con resolución del OIC (no grave)'
  },
  CONCLUIDA_AUTORIDAD: {
    backend: 'CONCLUIDA_AUTORIDAD',
    label: 'Concluida con resolución de la Autoridad Investigadora'
  },
  RECHAZADA_OIC: {
    backend: 'RECHAZADA_OIC',
    label: 'Rechazada por el OIC'
  },
  RECHAZADA_AUTORIDAD: {
    backend: 'RECHAZADA_AUTORIDAD',
    label: 'Rechazada por la Autoridad Investigadora'
  },
  TURNADA_AUTORIDAD: {
    backend: 'TURNADA_AUTORIDAD',
    label: 'Turnada a Autoridad Investigadora (falta grave)'
  },
  TURNADA_FISCALIA: {
    backend: 'TURNADA_FISCALIA',
    label: 'Turnada a Fiscalía Anticorrupción (corrupción)'
  },
  EN_ANALISIS: {
    backend: 'EN_ANALISIS',
    label: 'En análisis por OIC'
  }
}

  
  const headers = [
    { title: 'Folio', key: 'folio' },
    { title: 'Fecha de recepción', key: 'fecha' },
    { title: 'Días Transcurridos', key: 'dias_transcurridos' },
    { title: 'Estado de la denuncia', key: 'estado_denuncia' },
    { title: 'Dependencia Turnada', key: 'dependencia_turnada' }, // ✅ Nuevo campo
    { title: 'Fecha de última actualización', key: 'fecha_turno' },
    { title: 'Faltas No Graves', key: 'faltas_no_graves' },
    { title: 'Faltas Graves', key: 'faltas_graves' },
    { title: 'Hechos de Corrupción', key: 'hechos_corrupcion' },
    { title: 'Acciones', key: 'acciones', sortable: false }
  ]
  
  const obtenerLabelEstado = (clave) => {
    const match = Object.values(ESTADOS_VISIBLES).find(e => e.backend === clave)
    return match ? match.label : clave
  }

  const colorEstado = (estado) => {
  switch (estado) {
    case 'RECHAZADA':
      return 'red'
    case 'CONCLUIDA':
      return 'green'
    case 'TURNADA_FISCALIA':
      return 'deep-purple'
    case 'TURNADA_AUTORIDAD':
      return 'blue'
    default:
      return 'grey'
  }
}

  
  const filtrarDenuncias = () => {
    const token = localStorage.getItem('access_token')
    if (token) {
      const decoded = jwtDecode(token)
      estadoUsuario.value = decoded.estado
      denuncias.value = mockData.filter(d => d.ubicacion_hecho.estado === estadoUsuario.value)
    }
  }
  
  const denunciasFormateadas = computed(() => {
    return denuncias.value.map(d => {
      const fechaRecepcion = new Date(d.fecha_recepcion)
      const hoy = new Date()
      const diffDays = Math.floor((hoy - fechaRecepcion) / (1000 * 60 * 60 * 24))
  
      return {
        folio: d.folio || 'Sin folio',
        fecha: d.fecha_recepcion || 'Sin fecha',
        dias_transcurridos: diffDays,
        estado_denuncia: d.estado_denuncia || ESTADOS_VISIBLES.EN_ANALISIS.label,
        dependencia_turnada: d.dependencia_turnada || '—', // <- esto debe venir del backend si lo agregaste
        fecha_turno: d.fecha_turno || 'Sin fecha',
        faltas_graves: d.clasificacion_faltas?.faltas_graves || [],
        faltas_no_graves: d.clasificacion_faltas?.faltas_no_graves || [],
        hechos_corrupcion: d.clasificacion_faltas?.hechos_corrupcion || [],
        original: d
      }
    })
  })
  
  const historial = ref([])

  const mostrarDetalles = async (denuncia) => {
  denunciaSeleccionada.value = denuncia
  dialog.value = true

  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get(`${API_URL}/api/seguimientos/folio/${denuncia.folio}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    historial.value = res.data
  } catch (err) {
    console.error('❌ Error al cargar historial:', err)
    historial.value = []
  }
}

const actualizarSeguimiento = async (folio, estadoClave, comentario = '', dependencia_id = null) => {
  try {
    const token = localStorage.getItem('access_token')
    const payload = {
      folio,
      estado: estadoClave,
      comentario
    }
    if (dependencia_id) payload.dependencia_id = dependencia_id

    await axios.post(`${import.meta.env.VITE_API_URL}/api/seguimiento/`, payload, {
      headers: { Authorization: `Bearer ${token}` }
    })

    await refrescarDenuncias()
  } catch (error) {
    console.error('❌ Error al actualizar seguimiento:', error.response?.data || error)
  }
}


const confirmarTurnoAutoridad = async () => {
  if (!denunciaTurno.value || !dependenciaSeleccionada.value) return

  await actualizarSeguimiento(
    denunciaTurno.value.folio,
    ESTADOS_VISIBLES.TURNADA_AUTORIDAD.backend,
    comentarioTurno.value || 'Sin comentario',
    dependenciaSeleccionada.value
  )

  comentarioTurno.value = ''
  dialogTurno.value = false
}



const cargarSeguimientosDesdeBackend = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get(`${API_URL}/api/seguimientos/ultimos/`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    for (const d of denuncias.value) {
      const seguimiento = res.data.find(s => s.folio === d.folio)
      if (seguimiento) {
        d.estado_denuncia = obtenerLabelEstado(seguimiento.estado)

        const fechaValida = new Date(seguimiento.fecha_turno)
        d.fecha_turno = !isNaN(fechaValida)
          ? fechaValida.toLocaleString('es-MX', {
              year: 'numeric',
              month: '2-digit',
              day: '2-digit',
              hour: '2-digit',
              minute: '2-digit'
            }).replace(',', '')
          : 'Fecha inválida'

        // ✅ Agregar dependencia turnada si está disponible
        d.dependencia_turnada = seguimiento.dependencia?.nombre || '—'
      } else {
        d.estado_denuncia = ESTADOS_VISIBLES.EN_ANALISIS.label
        d.fecha_turno = 'Sin fecha'
        d.dependencia_turnada = '—'
      }
    }
  } catch (err) {
    console.error('❌ Error al cargar últimos seguimientos:', err)
  }
}
  

const abrirModalTurno = async (item) => {
  denunciaTurno.value = item
  dependenciaSeleccionada.value = null
  dialogTurno.value = true

  try {
    const token = localStorage.getItem('access_token')
    const decoded = jwtDecode(token)
    const estado = decoded.estado

    const res = await axios.get(`${import.meta.env.VITE_API_URL}/api/dependencias/AUTORIDAD_INVESTIGADORA/?estado=${estado}`, {
      headers: { Authorization: `Bearer ${token}` }
    })

    dependenciasInvestigadoras.value = res.data
  } catch (err) {
    console.error('❌ Error al cargar dependencias:', err)
    dependenciasInvestigadoras.value = []
  }
}


  const refrescarDenuncias = async () => {
    filtrarDenuncias()
    await cargarSeguimientosDesdeBackend()
  }
  
  const turnarAutoridad = (item) => {
    actualizarSeguimiento(item.folio, ESTADOS_VISIBLES.TURNADA_AUTORIDAD.backend)
  }
  
  const turnarFiscalia = (item) => {
    actualizarSeguimiento(item.folio, ESTADOS_VISIBLES.TURNADA_FISCALIA.backend)
  }
  
  const rechazarDenuncia = (item) => {
    denunciaRechazo.value = item
    comentarioRechazo.value = ''
    dialogRechazo.value = true
  }
  
  const confirmarRechazo = () => {
  if (denunciaRechazo.value) {
    actualizarSeguimiento(
      denunciaRechazo.value.folio,
      ESTADOS_VISIBLES.RECHAZADA_OIC.backend,
      comentarioRechazo.value || 'Sin comentario'
    )
    dialogRechazo.value = false
  }
}

  
  const abrirModalConclusion = (item) => {
    denunciaConclusion.value = item
    comentarioConclusion.value = ''
    dialogConclusion.value = true
  }
  
  const confirmarConclusion = () => {
  if (denunciaConclusion.value) {
    actualizarSeguimiento(
      denunciaConclusion.value.folio,
      ESTADOS_VISIBLES.CONCLUIDA_OIC.backend,
      comentarioConclusion.value || 'Sin resolución detallada'
    )
    dialogConclusion.value = false
  }
}

  onMounted(() => {
    refrescarDenuncias()
  })
  </script>
  