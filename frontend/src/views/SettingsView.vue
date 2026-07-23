<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/client'
import AppLayout from '@/components/AppLayout.vue'
import AppToast from '@/components/AppToast.vue'
import { useAuthStore, type User, type UserRole } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()

const firstName = ref('')
const lastName = ref('')
const avatarFile = ref<File | null>(null)
const profileLoading = ref(false)
const profileError = ref('')

const currentPassword = ref('')
const newPassword = ref('')
const confirmPassword = ref('')
const passwordLoading = ref(false)
const passwordError = ref('')

const users = ref<User[]>([])
const usersLoading = ref(false)
const usersError = ref('')
const toast = ref('')

const isAdmin = computed(() => auth.user?.role === 'admin')

const roles: { value: UserRole; label: string }[] = [
  { value: 'admin', label: 'Admin' },
  { value: 'recruiter', label: 'Recruiter' },
  { value: 'interviewer', label: 'Interviewer' },
  { value: 'hiring_manager', label: 'Hiring Manager' },
]

const inputClass =
  'mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-sqli-sky'

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => {
    toast.value = ''
  }, 2500)
}

function syncProfileForm() {
  firstName.value = auth.user?.first_name || ''
  lastName.value = auth.user?.last_name || ''
}

function onAvatarChange(e: Event) {
  const input = e.target as HTMLInputElement
  avatarFile.value = input.files?.[0] ?? null
}

async function saveProfile() {
  profileLoading.value = true
  profileError.value = ''
  try {
    if (avatarFile.value) {
      const form = new FormData()
      form.append('first_name', firstName.value.trim())
      form.append('last_name', lastName.value.trim())
      form.append('avatar', avatarFile.value)
      await auth.updateProfile(form)
    } else {
      await auth.updateProfile({
        first_name: firstName.value.trim(),
        last_name: lastName.value.trim(),
      })
    }
    avatarFile.value = null
    showToast('Profile updated.')
  } catch (err) {
    profileError.value = axios.isAxiosError(err)
      ? 'Could not update profile.'
      : 'Could not update profile.'
  } finally {
    profileLoading.value = false
  }
}

async function savePassword() {
  passwordLoading.value = true
  passwordError.value = ''
  try {
    await auth.changePassword({
      current_password: currentPassword.value,
      new_password: newPassword.value,
      confirm_password: confirmPassword.value,
    })
    currentPassword.value = ''
    newPassword.value = ''
    confirmPassword.value = ''
    showToast('Password updated.')
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const data = err.response?.data as Record<string, unknown> | undefined
      passwordError.value =
        (typeof data?.detail === 'string' && data.detail) ||
        (Array.isArray(data?.current_password) && String(data.current_password[0])) ||
        (Array.isArray(data?.confirm_password) && String(data.confirm_password[0])) ||
        (Array.isArray(data?.new_password) && String(data.new_password[0])) ||
        'Could not change password.'
    } else {
      passwordError.value = 'Could not change password.'
    }
  } finally {
    passwordLoading.value = false
  }
}

async function loadUsers() {
  if (!isAdmin.value) return
  usersLoading.value = true
  usersError.value = ''
  try {
    const { data } = await api.get<User[] | { results: User[] }>('/api/auth/users/', {
      params: { include_inactive: '1' },
    })
    users.value = Array.isArray(data) ? data : data.results ?? []
  } catch {
    usersError.value = 'Could not load users.'
  } finally {
    usersLoading.value = false
  }
}

async function updateUserRole(user: User, role: UserRole) {
  try {
    const { data } = await api.patch<User>(`/api/auth/users/${user.id}/`, { role })
    const idx = users.value.findIndex((u) => u.id === user.id)
    if (idx >= 0) users.value[idx] = { ...users.value[idx], ...data }
    showToast('Role updated.')
  } catch {
    showToast('Could not update role.')
  }
}

async function toggleActive(user: User) {
  try {
    const { data } = await api.patch<User>(`/api/auth/users/${user.id}/`, {
      is_active: !user.is_active,
    })
    const idx = users.value.findIndex((u) => u.id === user.id)
    if (idx >= 0) users.value[idx] = { ...users.value[idx], ...data }
    showToast(data.is_active ? 'User activated.' : 'User deactivated.')
  } catch {
    showToast('Could not update user.')
  }
}

onMounted(() => {
  syncProfileForm()
  loadUsers()
})
</script>

<template>
  <AppLayout>
    <h1 class="text-2xl font-semibold text-sqli-midnight mb-2">Settings</h1>
    <p class="text-gray-500 text-sm mb-8">Profile, password, and user management</p>

    <div class="space-y-6 max-w-3xl">
      <!-- Profile -->
      <form
        class="bg-white rounded-xl border border-sqli-gray-100 p-6 space-y-4"
        @submit.prevent="saveProfile"
      >
        <h2 class="font-medium text-sqli-midnight">Profile</h2>
        <div class="flex items-center gap-4">
          <img
            v-if="auth.user?.avatar_url"
            :src="auth.user.avatar_url"
            alt=""
            class="w-14 h-14 rounded-full object-cover"
          />
          <div
            v-else
            class="w-14 h-14 rounded-full bg-sqli-cobalt text-white flex items-center justify-center font-semibold"
          >
            {{ (auth.user?.first_name?.[0] || '') + (auth.user?.last_name?.[0] || '') }}
          </div>
          <label class="text-sm text-sqli-cobalt cursor-pointer hover:underline">
            Change avatar
            <input type="file" accept="image/*" class="hidden" @change="onAvatarChange" />
          </label>
        </div>
        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="text-sm text-gray-600" for="fn">First name</label>
            <input id="fn" v-model="firstName" :class="inputClass" required />
          </div>
          <div>
            <label class="text-sm text-gray-600" for="ln">Last name</label>
            <input id="ln" v-model="lastName" :class="inputClass" required />
          </div>
        </div>
        <p class="text-sm text-gray-500">Email: {{ auth.user?.email }} (read-only)</p>
        <p v-if="profileError" class="text-sm text-red-600">{{ profileError }}</p>
        <button
          type="submit"
          class="bg-sqli-cobalt text-white text-sm px-4 py-2 rounded-lg disabled:opacity-50"
          :disabled="profileLoading"
        >
          {{ profileLoading ? 'Saving…' : 'Save profile' }}
        </button>
      </form>

      <!-- Password -->
      <form
        class="bg-white rounded-xl border border-sqli-gray-100 p-6 space-y-4"
        @submit.prevent="savePassword"
      >
        <h2 class="font-medium text-sqli-midnight">Change password</h2>
        <div>
          <label class="text-sm text-gray-600" for="cur">Current password</label>
          <input
            id="cur"
            v-model="currentPassword"
            type="password"
            :class="inputClass"
            required
          />
        </div>
        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="text-sm text-gray-600" for="np">New password</label>
            <input id="np" v-model="newPassword" type="password" :class="inputClass" required />
          </div>
          <div>
            <label class="text-sm text-gray-600" for="cp">Confirm password</label>
            <input
              id="cp"
              v-model="confirmPassword"
              type="password"
              :class="inputClass"
              required
            />
          </div>
        </div>
        <p v-if="passwordError" class="text-sm text-red-600">{{ passwordError }}</p>
        <button
          type="submit"
          class="bg-sqli-cobalt text-white text-sm px-4 py-2 rounded-lg disabled:opacity-50"
          :disabled="passwordLoading"
        >
          {{ passwordLoading ? 'Updating…' : 'Update password' }}
        </button>
      </form>

      <!-- Admin users -->
      <div
        v-if="isAdmin"
        class="bg-white rounded-xl border border-sqli-gray-100 p-6 space-y-4"
      >
        <div class="flex items-center justify-between gap-3 flex-wrap">
          <h2 class="font-medium text-sqli-midnight">User management</h2>
          <button
            type="button"
            class="text-sm text-sqli-cobalt hover:underline"
            @click="router.push('/register')"
          >
            Create user
          </button>
        </div>
        <p v-if="usersLoading" class="text-sm text-gray-500">Loading…</p>
        <p v-else-if="usersError" class="text-sm text-red-600">{{ usersError }}</p>
        <div v-else class="overflow-x-auto">
          <table class="w-full text-sm text-left">
            <thead class="text-xs text-gray-400 uppercase border-b border-sqli-gray-100">
              <tr>
                <th class="py-2 pr-3">Name</th>
                <th class="py-2 pr-3">Email</th>
                <th class="py-2 pr-3">Role</th>
                <th class="py-2">Active</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="u in users"
                :key="u.id"
                class="border-b border-sqli-gray-100 last:border-0"
              >
                <td class="py-2.5 pr-3 text-sqli-midnight">
                  {{ u.first_name }} {{ u.last_name }}
                </td>
                <td class="py-2.5 pr-3 text-gray-500">{{ u.email }}</td>
                <td class="py-2.5 pr-3">
                  <select
                    class="rounded-lg border border-gray-200 px-2 py-1 text-sm bg-white"
                    :value="u.role"
                    @change="
                      updateUserRole(
                        u,
                        ($event.target as HTMLSelectElement).value as UserRole,
                      )
                    "
                  >
                    <option v-for="r in roles" :key="r.value" :value="r.value">
                      {{ r.label }}
                    </option>
                  </select>
                </td>
                <td class="py-2.5">
                  <button
                    type="button"
                    class="text-xs px-2 py-1 rounded-lg border"
                    :class="
                      u.is_active !== false
                        ? 'border-green-200 text-green-700 bg-green-50'
                        : 'border-gray-200 text-gray-500'
                    "
                    @click="toggleActive(u)"
                  >
                    {{ u.is_active !== false ? 'Active' : 'Inactive' }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <AppToast :message="toast" />
  </AppLayout>
</template>
