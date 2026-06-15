<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()
const health = ref<{ status: string; service: string } | null>(null)
const apiError = ref('')

onMounted(async () => {
  try {
    health.value = await auth.checkHealth()
  } catch {
    apiError.value = 'Backend not reachable. Run: make dev-backend'
  }
})

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex">
    <aside class="w-64 bg-sqli-midnight text-white p-6 flex flex-col">
      <div class="text-xl font-bold mb-1">SQLI</div>
      <p class="text-sqli-sky text-xs mb-8">Interview Tracker</p>
      <nav class="space-y-2 text-sm flex-1">
        <a class="block px-3 py-2 rounded-lg bg-white/10" href="#">Dashboard</a>
        <a class="block px-3 py-2 rounded-lg text-white/60" href="#">Candidates</a>
        <a class="block px-3 py-2 rounded-lg text-white/60" href="#">Jobs</a>
        <a class="block px-3 py-2 rounded-lg text-white/60" href="#">Interviews</a>
        <a class="block px-3 py-2 rounded-lg text-white/60" href="#">AI Tools</a>
      </nav>
      <button class="text-sm text-white/70 hover:text-white" @click="handleLogout">
        Logout
      </button>
    </aside>

    <main class="flex-1 p-8">
      <h1 class="text-2xl font-semibold text-sqli-midnight mb-2">Dashboard</h1>
      <p class="text-gray-500 mb-8">Scaffold ready — start with ticket INT-009.</p>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <p class="text-sm text-gray-500">Open Jobs</p>
          <p class="text-3xl font-bold text-sqli-cobalt mt-1">—</p>
        </div>
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <p class="text-sm text-gray-500">Active Candidates</p>
          <p class="text-3xl font-bold text-sqli-cobalt mt-1">—</p>
        </div>
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <p class="text-sm text-gray-500">Interviews This Week</p>
          <p class="text-3xl font-bold text-sqli-cobalt mt-1">—</p>
        </div>
      </div>

      <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
        <h2 class="font-medium text-sqli-midnight mb-2">API Status</h2>
        <p v-if="health" class="text-green-600 text-sm">
          ✓ Backend healthy — {{ health.service }}
        </p>
        <p v-else-if="apiError" class="text-amber-600 text-sm">{{ apiError }}</p>
        <p v-else class="text-gray-400 text-sm">Checking…</p>
      </div>
    </main>
  </div>
</template>
