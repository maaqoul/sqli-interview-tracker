<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { fetchJobs } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const health = ref<{ status: string; service: string } | null>(null)
const apiError = ref('')
const openJobsCount = ref<number | null>(null)

onMounted(async () => {
  try {
    health.value = await auth.checkHealth()
  } catch {
    apiError.value = 'Backend not reachable. Run: make dev-backend'
  }

  try {
    const data = await fetchJobs('open')
    openJobsCount.value = data.count
  } catch {
    openJobsCount.value = null
  }
})
</script>

<template>
  <AppLayout>
    <h1 class="text-2xl font-semibold text-sqli-midnight mb-2">Dashboard</h1>
    <p class="text-gray-500 mb-8">Overview of your hiring pipeline</p>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
      <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
        <p class="text-sm text-gray-500">Open Jobs</p>
        <p class="text-3xl font-bold text-sqli-cobalt mt-1">
          {{ openJobsCount ?? '—' }}
        </p>
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
  </AppLayout>
</template>
