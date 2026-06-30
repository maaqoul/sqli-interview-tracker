<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchJobs } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import AppToast from '@/components/AppToast.vue'
import JobStatusBadge from '@/components/JobStatusBadge.vue'
import { useAuthStore } from '@/stores/auth'
import type { Job } from '@/types/jobs'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const jobs = ref<Job[]>([])
const loading = ref(true)
const error = ref('')
const statusFilter = ref('')
const toast = ref('')

const canManageJobs = computed(
  () => auth.user?.role === 'recruiter' || auth.user?.role === 'admin',
)

const levelLabels: Record<string, string> = {
  junior: 'Junior',
  mid: 'Mid',
  senior: 'Senior',
  lead: 'Lead',
}

async function loadJobs() {
  loading.value = true
  error.value = ''
  try {
    const data = await fetchJobs(statusFilter.value || undefined)
    jobs.value = data.results
  } catch {
    error.value = 'Could not load jobs. Is the backend running?'
  } finally {
    loading.value = false
  }
}

function showToastFromQuery() {
  const msg = route.query.toast
  if (typeof msg === 'string' && msg) {
    toast.value = msg
    router.replace({ query: {} })
    setTimeout(() => {
      toast.value = ''
    }, 3000)
  }
}

onMounted(() => {
  loadJobs()
  showToastFromQuery()
})

watch(statusFilter, loadJobs)
watch(() => route.query.toast, showToastFromQuery)
</script>

<template>
  <AppLayout>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-semibold text-sqli-midnight">Job Openings</h1>
        <p class="text-gray-500 text-sm mt-1">Manage open roles and hiring pipelines</p>
      </div>
      <router-link
        v-if="canManageJobs"
        to="/jobs/new"
        class="bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-4 py-2.5 rounded-lg transition-colors"
      >
        + Create Job
      </router-link>
    </div>

    <div class="mb-4">
      <select
        v-model="statusFilter"
        class="rounded-lg border border-gray-200 px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sqli-sky"
      >
        <option value="">All statuses</option>
        <option value="open">Open</option>
        <option value="on_hold">On hold</option>
        <option value="closed">Closed</option>
      </select>
    </div>

    <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>

    <div
      v-if="loading"
      class="bg-white rounded-xl border border-sqli-gray-100 p-8 text-center text-gray-500"
    >
      Loading jobs…
    </div>

    <div
      v-else-if="jobs.length === 0"
      class="bg-white rounded-xl border border-sqli-gray-100 p-12 text-center"
    >
      <p class="text-sqli-midnight font-medium mb-2">No job openings yet</p>
      <p class="text-gray-500 text-sm mb-6">
        We Elevate. Digitally. — start by creating your first role.
      </p>
      <router-link
        v-if="canManageJobs"
        to="/jobs/new"
        class="inline-block bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-4 py-2.5 rounded-lg"
      >
        Create your first job
      </router-link>
    </div>

    <div v-else class="bg-white rounded-xl border border-sqli-gray-100 overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-sqli-gray-100/50 text-left text-gray-600">
          <tr>
            <th class="px-4 py-3 font-medium">Title</th>
            <th class="px-4 py-3 font-medium">Department</th>
            <th class="px-4 py-3 font-medium">Location</th>
            <th class="px-4 py-3 font-medium">Level</th>
            <th class="px-4 py-3 font-medium">Status</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="job in jobs"
            :key="job.id"
            class="border-t border-sqli-gray-100 hover:bg-sqli-cream/50 cursor-pointer"
            @click="router.push(`/jobs/${job.id}`)"
          >
            <td class="px-4 py-3 font-medium text-sqli-midnight">{{ job.title }}</td>
            <td class="px-4 py-3 text-gray-600">{{ job.department }}</td>
            <td class="px-4 py-3 text-gray-600">{{ job.location }}</td>
            <td class="px-4 py-3 text-gray-600">{{ levelLabels[job.level] }}</td>
            <td class="px-4 py-3">
              <JobStatusBadge :status="job.status" />
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <AppToast :message="toast" />
  </AppLayout>
</template>
