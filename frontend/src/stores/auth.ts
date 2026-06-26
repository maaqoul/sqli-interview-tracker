import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/api/client'

export type UserRole = 'admin' | 'recruiter' | 'interviewer' | 'hiring_manager'

export interface User {
  id: number
  email: string
  role: UserRole
  first_name: string
  last_name: string
}

interface LoginResponse {
  access: string
  refresh: string
}

export interface RegisterPayload {
  email: string
  password: string
  first_name: string
  last_name: string
  role: UserRole
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isAuthenticated = ref(!!localStorage.getItem('access_token'))

  function setTokens(access: string, refresh: string) {
    localStorage.setItem('access_token', access)
    localStorage.setItem('refresh_token', refresh)
    isAuthenticated.value = true
  }

  function clearTokens() {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    isAuthenticated.value = false
  }

  async function fetchUser() {
    const { data } = await api.get<User>('/api/auth/me/')
    user.value = data
    return data
  }

  async function login(email: string, password: string) {
    const { data } = await api.post<LoginResponse>('/api/auth/login/', {
      email,
      password,
    })
    setTokens(data.access, data.refresh)
    await fetchUser()
  }

  async function register(payload: RegisterPayload) {
    const { data } = await api.post<User>('/api/auth/register/', payload)
    return data
  }

  async function refresh() {
    const refreshToken = localStorage.getItem('refresh_token')
    if (!refreshToken) {
      throw new Error('No refresh token')
    }

    const { data } = await api.post<{ access: string }>('/api/auth/refresh/', {
      refresh: refreshToken,
    })
    localStorage.setItem('access_token', data.access)
    isAuthenticated.value = true
    return data.access
  }

  function logout() {
    clearTokens()
    user.value = null
  }

  async function initialize() {
    if (!localStorage.getItem('access_token')) {
      return
    }

    try {
      await fetchUser()
    } catch {
      logout()
    }
  }

  async function checkHealth() {
    const { data } = await api.get('/api/health/')
    return data
  }

  return {
    user,
    isAuthenticated,
    login,
    logout,
    register,
    refresh,
    fetchUser,
    initialize,
    checkHealth,
  }
})
