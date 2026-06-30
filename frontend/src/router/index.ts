import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '@/views/LoginView.vue'
import RegisterView from '@/views/RegisterView.vue'
import DashboardView from '@/views/DashboardView.vue'
import JobsListView from '@/views/jobs/JobsListView.vue'
import JobDetailView from '@/views/jobs/JobDetailView.vue'
import JobFormView from '@/views/jobs/JobFormView.vue'
import { useAuthStore } from '@/stores/auth'

declare module 'vue-router' {
  interface RouteMeta {
    public?: boolean
    requiresAdmin?: boolean
    requiresRecruiter?: boolean
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
    { path: '/jobs', name: 'jobs', component: JobsListView },
    {
      path: '/jobs/new',
      name: 'job-create',
      component: JobFormView,
      meta: { requiresRecruiter: true },
    },
    {
      path: '/jobs/:id/edit',
      name: 'job-edit',
      component: JobFormView,
      meta: { requiresRecruiter: true },
    },
    { path: '/jobs/:id', name: 'job-detail', component: JobDetailView },
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

  if (
    to.meta.requiresRecruiter &&
    auth.user?.role !== 'recruiter' &&
    auth.user?.role !== 'admin'
  ) {
    return { name: 'jobs' }
  }

  return true
})

export default router
