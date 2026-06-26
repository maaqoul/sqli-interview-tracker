<script setup lang="ts">
import axios from 'axios'
import { ref } from 'vue'
import AuthBrandHeader from '@/components/AuthBrandHeader.vue'
import { useAuthStore, type UserRole } from '@/stores/auth'

const auth = useAuthStore()

const firstName = ref('')
const lastName = ref('')
const email = ref('')
const password = ref('')
const role = ref<UserRole>('recruiter')

const firstNameError = ref('')
const lastNameError = ref('')
const emailError = ref('')
const passwordError = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const roles: { value: UserRole; label: string }[] = [
  { value: 'admin', label: 'Admin' },
  { value: 'recruiter', label: 'Recruiter' },
  { value: 'interviewer', label: 'Interviewer' },
  { value: 'hiring_manager', label: 'Hiring Manager' },
]

const inputClass =
  'mt-1 w-full rounded-lg border px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky'
const inputErrorClass = `${inputClass} border-red-400`
const inputNormalClass = `${inputClass} border-gray-200`

function validate(): boolean {
  firstNameError.value = ''
  lastNameError.value = ''
  emailError.value = ''
  passwordError.value = ''
  error.value = ''
  success.value = ''

  let valid = true

  if (!firstName.value.trim()) {
    firstNameError.value = 'First name is required.'
    valid = false
  }

  if (!lastName.value.trim()) {
    lastNameError.value = 'Last name is required.'
    valid = false
  }

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

function parseApiError(err: unknown): string {
  if (!axios.isAxiosError(err)) {
    return 'Could not create user. Please try again.'
  }

  if (err.response?.status === 403) {
    return 'Only admins can create users.'
  }

  const data = err.response?.data
  if (typeof data === 'object' && data !== null) {
    const messages = Object.values(data).flat()
    if (messages.length > 0) {
      return String(messages[0])
    }
  }

  return 'Could not create user. Please try again.'
}

async function handleRegister() {
  if (!validate()) return

  loading.value = true
  try {
    await auth.register({
      email: email.value.trim(),
      password: password.value,
      first_name: firstName.value.trim(),
      last_name: lastName.value.trim(),
      role: role.value,
    })

    success.value = `User ${email.value.trim()} created successfully.`
    firstName.value = ''
    lastName.value = ''
    email.value = ''
    password.value = ''
    role.value = 'recruiter'
  } catch (err: unknown) {
    error.value = parseApiError(err)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="min-h-screen flex items-center justify-center bg-sqli-cream px-4 py-8">
    <div class="w-full max-w-md">
      <AuthBrandHeader />

      <form
        class="bg-white rounded-xl shadow-sm border border-sqli-gray-100 p-8"
        @submit.prevent="handleRegister"
      >
        <h1 class="text-xl font-semibold text-sqli-midnight mb-1">Create user</h1>
        <p class="text-sm text-gray-500 mb-6">Admin only — add a new team member.</p>

        <div class="grid grid-cols-2 gap-4 mb-4">
          <label class="block">
            <span class="text-sm text-gray-600">First name</span>
            <input
              v-model="firstName"
              type="text"
              autocomplete="given-name"
              :class="firstNameError ? inputErrorClass : inputNormalClass"
              @input="firstNameError = ''"
            />
            <p v-if="firstNameError" class="text-red-500 text-sm mt-1">{{ firstNameError }}</p>
          </label>

          <label class="block">
            <span class="text-sm text-gray-600">Last name</span>
            <input
              v-model="lastName"
              type="text"
              autocomplete="family-name"
              :class="lastNameError ? inputErrorClass : inputNormalClass"
              @input="lastNameError = ''"
            />
            <p v-if="lastNameError" class="text-red-500 text-sm mt-1">{{ lastNameError }}</p>
          </label>
        </div>

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
            autocomplete="new-password"
            :class="passwordError ? inputErrorClass : inputNormalClass"
            @input="passwordError = ''"
          />
          <p v-if="passwordError" class="text-red-500 text-sm mt-1">{{ passwordError }}</p>
        </label>

        <label class="block mb-6">
          <span class="text-sm text-gray-600">Role</span>
          <select
            v-model="role"
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky bg-white"
          >
            <option v-for="option in roles" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </label>

        <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>
        <p v-if="success" class="text-green-600 text-sm mb-4">{{ success }}</p>

        <button
          type="submit"
          :disabled="loading"
          class="w-full bg-sqli-cobalt hover:bg-[#003399] text-white font-medium py-2.5 rounded-lg transition-colors disabled:opacity-50"
        >
          {{ loading ? 'Creating…' : 'Create user' }}
        </button>

        <router-link
          to="/dashboard"
          class="block text-center text-sm text-sqli-cobalt hover:underline mt-4"
        >
          Back to dashboard
        </router-link>
      </form>
    </div>
  </div>
</template>
