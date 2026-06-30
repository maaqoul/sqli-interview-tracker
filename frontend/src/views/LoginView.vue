<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import AuthBrandHeader from '@/components/AuthBrandHeader.vue'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const email = ref('')
const password = ref('')
const emailError = ref('')
const passwordError = ref('')
const error = ref('')
const loading = ref(false)

const inputClass =
  'mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky'
const inputErrorClass = `${inputClass} border-red-400`
const inputNormalClass = `${inputClass} border-gray-200`

function validate(): boolean {
  emailError.value = ''
  passwordError.value = ''
  error.value = ''

  let valid = true

  const trimmedEmail = email.value.trim()
  if (!trimmedEmail) {
    emailError.value = 'Email is required.'
    valid = false
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(trimmedEmail)) {
    emailError.value = 'Enter a valid email address.'
    valid = false
  }

  if (!password.value) {
    passwordError.value = 'Password is required.'
    valid = false
  } else if (password.value.length < 8) {
    passwordError.value = 'Password must be at least 8 characters.'
    valid = false
  }

  return valid
}

async function handleLogin() {
  if (!validate()) return

  loading.value = true
  try {
    await auth.login(email.value.trim(), password.value)
    await router.push('/dashboard')
  } catch (err: unknown) {
    error.value =
      axios.isAxiosError(err) && err.response?.status === 401
        ? 'Invalid email or password.'
        : 'Login failed. Please try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-sqli-cream px-4">
    <div class="w-full max-w-md">
      <AuthBrandHeader />

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
            autocomplete="email"
            :class="emailError ? inputErrorClass : inputNormalClass"
            @input="emailError = ''"
          />
          <p v-if="emailError" class="text-red-500 text-sm mt-1">{{ emailError }}</p>
        </label>

        <label class="block mb-4">
          <span class="text-sm text-gray-600">Password</span>
          <input
            v-model="password"
            type="password"
            autocomplete="current-password"
            :class="passwordError ? inputErrorClass : inputNormalClass"
            @input="passwordError = ''"
          />
          <p v-if="passwordError" class="text-red-500 text-sm mt-1">{{ passwordError }}</p>
        </label>

        <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-sqli-cobalt hover:bg-[#003399] text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50"
        >
          {{ loading ? 'Signing in…' : 'Sign in' }}
        </button>
      </form>
    </div>
  </div>
</template>
