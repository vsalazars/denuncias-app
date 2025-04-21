import { createRouter, createWebHistory } from 'vue-router'
import { jwtDecode } from 'jwt-decode'
import LoginView from '@/views/LoginView.vue'
import AdminDashboard from '@/views/AdminDashboard.vue'
import OicDashboard from '@/views/OicDashboard.vue'
import FiscaliaDashboard from '@/views/FiscaliaDashboard.vue'
import AutoridadDashboard from '@/views/AutoridadDashboard.vue'
import UsuarioDashboard from '@/views/UsuarioDashboard.vue'

const routes = [
  {
    path: '/',
    name: 'Login',
    component: LoginView,
  },
  {
    path: '/admin-dashboard',
    name: 'AdminDashboard',
    component: AdminDashboard,
    meta: { requiresAuth: true, role: 'ADMIN' },
  },
  {
    path: '/oic-dashboard',
    name: 'OicDashboard',
    component: OicDashboard,
    meta: { requiresAuth: true, role: 'OIC' },
  },
  {
    path: '/fiscalia-dashboard',
    name: 'FiscaliaDashboard',
    component: FiscaliaDashboard,
    meta: { requiresAuth: true, role: 'FISCALIA' },
  },
  {
    path: '/autoridad-dashboard',
    name: 'AutoridadDashboard',
    component: AutoridadDashboard,
    meta: { requiresAuth: true, role: 'AUTORIDAD_INVESTIGADORA' },
  },
  {
    path: '/usuario-dashboard',
    name: 'UsuarioDashboard',
    component: UsuarioDashboard,
    meta: { requiresAuth: true, role: 'DENUNCIANTE' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

// 🔒 Protección de rutas por rol
router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('access_token')
  if (!token && to.meta.requiresAuth) {
    return next('/')
  }

  if (token) {
    try {
      const decoded = jwtDecode(token)
      const userRole = decoded.rol

      if (to.meta.requiresAuth && to.meta.role && to.meta.role !== userRole) {
        return next('/') // rol no permitido
      }
    } catch (e) {
      console.error('Token inválido', e)
      return next('/')
    }
  }

  next()
})

export default router
