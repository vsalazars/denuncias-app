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
          <v-btn color="blue" small class="ma-1" @click="turnarAutoridad(item)">Turnar a Autoridad</v-btn>
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

      <v-timeline side="end" dense>
        <v-timeline-item
          v-for="(item, index) in historial"
          :key="index"
          :dot-color="colorEstado(item.estado)"
          size="small"
        >
          <strong>{{ obtenerLabelEstado(item.estado) }}</strong><br />
          <span class="text-caption">{{ new Date(item.fecha_turno).toLocaleString('es-MX') }}</span><br />
          <span v-if="item.comentario">📝 {{ item.comentario }}</span>
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
    </DashboardLayout>
  </template>
  
  <script setup>
  import { ref, onMounted, computed } from 'vue'
  import { jwtDecode } from 'jwt-decode'
  import DashboardLayout from '@/layouts/DashboardLayout.vue'
  import mockData from '@/fixtures/mock_denuncias.json'
  import axios from 'axios'
  
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
  
  // Mapeo de claves (para backend) y etiquetas (para frontend)
  const ESTADOS_VISIBLES = {
    CONCLUIDA: {
      backend: 'CONCLUIDA',
      label: 'Concluida con resolución del OIC (no grave)'
    },
    TURNADA_AUTORIDAD: {
      backend: 'TURNADA_AUTORIDAD',
      label: 'Turnada a Autoridad Investigadora (falta grave)'
    },
    TURNADA_FISCALIA: {
      backend: 'TURNADA_FISCALIA',
      label: 'Turnada a Fiscalía Anticorrupción (corrupción)'
    },
    RECHAZADA: {
      backend: 'RECHAZADA',
      label: 'Rechazada por falta de elementos'
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
    { title: 'Estado', key: 'estado_denuncia' },
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
    const res = await axios.get(`http://172.31.64.137:8000/api/seguimientos/folio/${denuncia.folio}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    historial.value = res.data
  } catch (err) {
    console.error('❌ Error al cargar historial:', err)
    historial.value = []
  }
}

  
  const actualizarSeguimiento = async (folio, estadoClave, comentario = '') => {
    try {
      const token = localStorage.getItem('access_token')
      console.log('📤 Enviando seguimiento:', {
        folio,
        estado: estadoClave,
        comentario
      })
  
      await axios.post('http://172.31.64.137:8000/api/seguimiento/', {
        folio,
        estado: estadoClave,
        comentario
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
  
      await refrescarDenuncias()
    } catch (error) {
      console.error('❌ Error al actualizar seguimiento:', error.response?.data || error)
    }
  }
  
  const cargarSeguimientosDesdeBackend = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const res = await axios.get('http://172.31.64.137:8000/api/seguimientos/ultimos/', {
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
      } else {
        d.estado_denuncia = ESTADOS_VISIBLES.EN_ANALISIS.label
        d.fecha_turno = 'Sin fecha'
      }
    }
  } catch (err) {
    console.error('❌ Error al cargar últimos seguimientos:', err)
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
        ESTADOS_VISIBLES.RECHAZADA.backend,
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
        ESTADOS_VISIBLES.CONCLUIDA.backend,
        comentarioConclusion.value || 'Sin resolución detallada'
      )
      dialogConclusion.value = false
    }
  }

  

  
  onMounted(() => {
    refrescarDenuncias()
  })
  </script>
  