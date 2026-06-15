<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const email = ref('recruiter@sqli.com')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  error.value = ''
  loading.value = true
  try {
    await auth.login(email.value, password.value)
    await router.push('/dashboard')
  } catch {
    error.value = 'Login failed. Auth API not wired yet — see ticket INT-010.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-sqli-cream px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <div class="text-3xl font-bold text-sqli-midnight tracking-tight">SQLI</div>
        <p class="text-sqli-cobalt mt-2 text-sm font-medium">We Elevate. Digitally.</p>
        <p class="text-gray-500 mt-1 text-sm">Interview Tracker</p>
      </div>

      <form
        class="bg-white rounded-xl shadow-sm border border-sqli-gray-100 p-8"
        @submit.prevent="handleLogin"
      >
        <h1 class="text-xl font-semibold text-sqli-midnight mb-6">Sign in</h1>

        <label class="block mb-4">
          <span class="text-sm text-gray-600">Email</span>
          <input
            v-model="email"
            type="email"
            required
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky"
          />
        </label>

        <label class="block mb-6">
          <span class="text-sm text-gray-600">Password</span>
          <input
            v-model="password"
            type="password"
            required
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky"
          />
        </label>

        <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-sqli-cobalt hover:bg-blue-800 text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50"
        >
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>
