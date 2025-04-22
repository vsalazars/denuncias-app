<template>
  <DashboardLayout>
    <h1>🕵️ Panel de la Autoridad Investigadora</h1>
    <p>Estado asignado: {{ estadoUsuario }}</p>

    <v-data-table
      :headers="headers"
      :items="denunciasFormateadas"
      class="elevation-1"
    >
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
        <v-chip
          v-for="(f, i) in item.faltas_graves"
          :key="i"
          color="red"
          class="ma-1"
          size="small"
        >
          {{ f }}
        </v-chip>
      </template>

      <template #item.faltas_no_graves="{ item }">
        <v-chip
          v-for="(f, i) in item.faltas_no_graves"
          :key="i"
          color="orange"
          class="ma-1"
          size="small"
        >
          {{ f }}
        </v-chip>
      </template>

      <template #item.hechos_corrupcion="{ item }">
        <v-chip
          v-for="(f, i) in item.hechos_corrupcion"
          :key="i"
          color="deep-purple"
          class="ma-1"
          size="small"
        >
          {{ f }}
        </v-chip>
      </template>

      <template #item.acciones="{ item }">
        <v-btn
          color="green"
          small
          class="ma-1"
          @click="abrirModalConclusion(item)"
        >
          Concluir con resolución
        </v-btn>
        <v-btn
          color="red"
          small
          class="ma-1"
          @click="abrirModalRechazo(item)"
        >
          Rechazar (volver al OIC)
        </v-btn>
      </template>
    </v-data-table>

    <!-- Modal Detalles -->
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
              v-for="(s, i) in historial"
              :key="i"
              :dot-color="colorEstado(s.estado)"
              size="small"
            >
              <strong>{{ obtenerLabelEstado(s.estado) }}</strong><br />
              <span class="text-caption">
                {{ new Date(s.fecha_turno).toLocaleString('es-MX') }}
              </span><br />
              <span
                v-if="s.comentario && !s.comentario.includes('ID')"
              >
                📝 {{ s.comentario }}
              </span><br />
              <span v-if="s.dependencia">🏛️ {{ s.dependencia.nombre }}</span>
            </v-timeline-item>
          </v-timeline>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialog = false">Cerrar</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal Rechazo -->
    <v-dialog v-model="dialogRechazo" max-width="600">
      <v-card>
        <v-card-title class="text-h6">❌ Rechazar Denuncia</v-card-title>
        <v-card-text>
          <p><strong>Folio:</strong> {{ denunciaRechazo?.folio }}</p>
          <v-textarea
            v-model="comentarioRechazo"
            label="Motivo del rechazo"
            rows="4"
            auto-grow
            outlined
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialogRechazo = false">Cancelar</v-btn>
          <v-btn color="red" @click="confirmarRechazo">Confirmar Rechazo</v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- Modal Conclusión -->
    <v-dialog v-model="dialogConclusion" max-width="600">
      <v-card>
        <v-card-title class="text-h6">✅ Concluir Denuncia</v-card-title>
        <v-card-text>
          <p><strong>Folio:</strong> {{ denunciaConclusion?.folio }}</p>
          <v-textarea
            v-model="comentarioConclusion"
            label="Resumen de la resolución"
            rows="4"
            auto-grow
            outlined
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn text @click="dialogConclusion = false">Cancelar</v-btn>
          <v-btn color="green" @click="confirmarConclusion">
            Confirmar Conclusión
          </v-btn>
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

// —————————————— estado reactivo ——————————————
const estadoUsuario      = ref('')
const dependenciaId      = ref(null)
const denuncias          = ref([])

const dialog             = ref(false)
const dialogRechazo      = ref(false)
const dialogConclusion   = ref(false)

const denunciaSeleccionada = ref(null)
const denunciaRechazo      = ref(null)
const comentarioRechazo    = ref('')
const denunciaConclusion   = ref(null)
const comentarioConclusion = ref('')

const historial = ref([])

// ————————— catálogo de estados —————————————
const ESTADOS_VISIBLES = {
  CONCLUIDA_OIC:       { backend:'CONCLUIDA_OIC',       label:'Concluida con resolución del OIC (no grave)' },
  CONCLUIDA_AUTORIDAD: { backend:'CONCLUIDA_AUTORIDAD', label:'Concluida con resolución de la Autoridad Investigadora' },
  RECHAZADA_OIC:       { backend:'RECHAZADA_OIC',       label:'Rechazada por el OIC' },
  RECHAZADA_AUTORIDAD: { backend:'RECHAZADA_AUTORIDAD', label:'Rechazada por la Autoridad Investigadora' },
  TURNADA_AUTORIDAD:   { backend:'TURNADA_AUTORIDAD',   label:'Turnada a Autoridad Investigadora (falta grave)' },
  TURNADA_FISCALIA:    { backend:'TURNADA_FISCALIA',    label:'Turnada a Fiscalía Anticorrupción (corrupción)' },
  EN_ANALISIS:         { backend:'EN_ANALISIS',         label:'En análisis por OIC' }
}

const obtenerLabelEstado = clave =>
  (Object.values(ESTADOS_VISIBLES).find(e => e.backend === clave) || {}).label || clave

// color por estado
const colorEstado = estado => ({
  RECHAZADA: 'red',
  CONCLUIDA: 'green',
  TURNADA_FISCALIA: 'deep-purple',
  TURNADA_AUTORIDAD: 'blue'
}[estado] || 'grey')

// —————————— Headers tabla ——————————————
const headers = [
  { title:'Folio',                 key:'folio' },
  { title:'Fecha de recepción',    key:'fecha' },
  { title:'Días Transcurridos',    key:'dias_transcurridos' },
  { title:'Estado de la denuncia', key:'estado_denuncia' },
  { title:'Dependencia Turnada',   key:'dependencia_turnada' },
  { title:'Fecha de última actualización', key:'fecha_turno' },
  { title:'Faltas No Graves',      key:'faltas_no_graves' },
  { title:'Faltas Graves',         key:'faltas_graves' },
  { title:'Hechos de Corrupción',  key:'hechos_corrupcion' },
  { title:'Acciones',              key:'acciones', sortable:false }
]

// —————— carga inicial desde mock + token ——————
function filtrarDenuncias() {
  const token = localStorage.getItem('access_token')
  if (!token) return
  const decoded = jwtDecode(token)
  estadoUsuario.value  = decoded.estado
  dependenciaId.value  = decoded.dependencia_id
  denuncias.value      = mockData.filter(d =>
    d.ubicacion_hecho.estado === estadoUsuario.value
  )
}

// —————— formato para la tabla ——————
const denunciasFormateadas = computed(() =>
  denuncias.value
    .filter(d => d.ultima_dependencia_id === dependenciaId.value)
    .map(d => {
      const dias = Math.floor((Date.now() - new Date(d.fecha_recepcion)) / 8.64e7)
      return {
        folio: d.folio || 'Sin folio',
        fecha: d.fecha_recepcion || 'Sin fecha',
        dias_transcurridos: dias,
        estado_denuncia: d.estado_denuncia,
        dependencia_turnada: d.dependencia_turnada || '—',
        fecha_turno: d.fecha_turno || 'Sin fecha',
        faltas_graves: d.clasificacion_faltas?.faltas_graves || [],
        faltas_no_graves: d.clasificacion_faltas?.faltas_no_graves || [],
        hechos_corrupcion: d.clasificacion_faltas?.hechos_corrupcion || [],
        acciones: '',
        original: d
      }
    })
)

// ————————— API —————————
async function actualizarSeguimiento(folio, estadoClave, comentario='', dependencia_id=null) {
  try {
    const token = localStorage.getItem('access_token')
    const payload = { folio, estado: estadoClave, comentario }
    if (dependencia_id) payload.dependencia_id = dependencia_id
    await axios.post(`${API_URL}/api/seguimiento/`, payload, {
      headers: { Authorization:`Bearer ${token}` }
    })
    await cargarSeguimientosDesdeBackend()
  } catch(e) {
    console.error('❌ Error al actualizar seguimiento:', e.response?.data||e)
  }
}

// —————— acciones UI ——————
function abrirModalConclusion(item) {
  denunciaConclusion.value = item
  dialogConclusion.value   = true
}
function abrirModalRechazo(item) {
  denunciaRechazo.value = item
  dialogRechazo.value   = true
}

function confirmarConclusion() {
  if (!denunciaConclusion.value) return
  actualizarSeguimiento(
    denunciaConclusion.value.folio,
    ESTADOS_VISIBLES.CONCLUIDA_AUTORIDAD.backend,
    comentarioConclusion.value || 'Sin resolución detallada',
    dependenciaId.value
  )
  dialogConclusion.value = false
}

function confirmarRechazo() {
  if (!denunciaRechazo.value) return
  actualizarSeguimiento(
    denunciaRechazo.value.folio,
    ESTADOS_VISIBLES.RECHAZADA_AUTORIDAD.backend,
    comentarioRechazo.value || 'Sin comentario',
    dependenciaId.value
  )
  dialogRechazo.value = false
}

// —————— carga últimos seguimientos del backend ——————
async function cargarSeguimientosDesdeBackend() {
  try {
    const token = localStorage.getItem('access_token')
    const { data } = await axios.get(
      `${API_URL}/api/seguimientos/ultimos/`,
      { headers:{ Authorization:`Bearer ${token}` } }
    )
    denuncias.value.forEach(d => {
      const seg = data.find(s => s.folio === d.folio)
      if (seg) {
        d.estado_denuncia       = obtenerLabelEstado(seg.estado)
        d.fecha_turno           = new Date(seg.fecha_turno).toLocaleString('es-MX')
        d.dependencia_turnada   = seg.dependencia?.nombre || '—'
        d.ultima_dependencia_id = seg.dependencia?.id || null
      } else {
        d.estado_denuncia       = ESTADOS_VISIBLES.EN_ANALISIS.label
        d.fecha_turno           = 'Sin fecha'
        d.dependencia_turnada   = '—'
        d.ultima_dependencia_id = null
      }
    })
  } catch(e) {
    console.error('❌ Error al cargar seguimientos:', e)
  }
}

// —————— timeline modal ——————
async function mostrarDetalles(d) {
  denunciaSeleccionada.value = d
  dialog.value               = true
  try {
    const token = localStorage.getItem('access_token')
    const { data } = await axios.get(
      `${API_URL}/api/seguimientos/folio/${d.folio}`,
      { headers:{ Authorization:`Bearer ${token}` } }
    )
    historial.value = data
  } catch(e) {
    console.error('❌ Error al cargar historial:', e)
    historial.value = []
  }
}

// —————— mount ——————
async function refrescarDenuncias() {
  filtrarDenuncias()
  await cargarSeguimientosDesdeBackend()
}

onMounted(refrescarDenuncias)
</script>
