import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export const useAuthStore = defineStore('auth', () => {
  const user = ref<{ email: string } | null>(null)
  const isAuthenticated = ref(!!localStorage.getItem('access_token'))

  async function login(email: string, password: string) {
    // INT-010: wire to POST /api/auth/login/
    void email
    void password
    // Placeholder until auth is implemented
    localStorage.setItem('access_token', 'dev-placeholder')
    isAuthenticated.value = true
    user.value = { email }
  }

  function logout() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    user.value = null
    isAuthenticated.value = false
  }

  async function checkHealth() {
    const { data } = await api.get('/api/health/')
    return data
  }

  return { user, isAuthenticated, login, logout, checkHealth }
})
