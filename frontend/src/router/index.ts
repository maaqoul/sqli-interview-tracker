import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    requiresAdmin?: boolean
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', redirect: '/dashboard' },
    { path: '/login', name: 'login', component: LoginView, meta: { public: true } },
    {
      path: '/register',
      name: 'register',
      component: RegisterView,
      meta: { requiresAdmin: true },
    },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  const isAuthenticated = auth.isAuthenticated

  if (to.meta.public) {
    if (to.name === 'login' && isAuthenticated) {
      return { name: 'dashboard' }
    }
    return true
  }

  if (!isAuthenticated) {
    return { name: 'login' }
  }

  if (!auth.user) {
    try {
      await auth.fetchUser()
    } catch {
      auth.logout()
      return { name: 'login' }
    }
  }

  if (to.meta.requiresAdmin && auth.user?.role !== 'admin') {
    return { name: 'dashboard' }
  }

  return true
})

export default router
