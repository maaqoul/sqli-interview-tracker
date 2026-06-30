<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchJob, fetchJobStages } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import AppToast from '@/components/AppToast.vue'
import JobStatusBadge from '@/components/JobStatusBadge.vue'
import { useAuthStore } from '@/stores/auth'
import type { Job, PipelineStage } from '@/types/jobs'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const job = ref<Job | null>(null)
const stages = ref<PipelineStage[]>([])
const loading = ref(true)
const error = ref('')
const toast = ref('')

const jobId = computed(() => Number(route.params.id))

const canManageJobs = computed(
  () => auth.user?.role === 'recruiter' || auth.user?.role === 'admin',
)

const levelLabels: Record<string, string> = {
  junior: 'Junior',
  mid: 'Mid',
  senior: 'Senior',
  lead: 'Lead',
}

onMounted(async () => {
  try {
    const [jobData, stageData] = await Promise.all([
      fetchJob(jobId.value),
      fetchJobStages(jobId.value),
    ])
    job.value = jobData
    stages.value = stageData
  } catch {
    error.value = 'Job not found or you do not have access.'
  } finally {
    loading.value = false
  }
  showToastFromQuery()
})

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

watch(() => route.query.toast, showToastFromQuery)
</script>

<template>
  <AppLayout>
    <router-link to="/jobs" class="text-sm text-sqli-cobalt hover:underline mb-4 inline-block">
      ← Back to jobs
    </router-link>

    <p v-if="loading" class="text-gray-500">Loading…</p>
    <p v-else-if="error" class="text-red-500 text-sm">{{ error }}</p>

    <template v-else-if="job">
      <div class="flex items-start justify-between mb-6">
        <div>
          <h1 class="text-2xl font-semibold text-sqli-midnight">{{ job.title }}</h1>
          <p class="text-gray-500 mt-1">
            {{ job.department }} · {{ job.location }} · {{ levelLabels[job.level] }}
          </p>
        </div>
        <div class="flex items-center gap-3">
          <JobStatusBadge :status="job.status" />
          <router-link
            v-if="canManageJobs"
            :to="`/jobs/${job.id}/edit`"
            class="text-sm text-sqli-cobalt hover:underline"
          >
            Edit
          </router-link>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div class="lg:col-span-2 space-y-6">
          <div class="bg-white rounded-xl border border-sqli-gray-100 p-6">
            <h2 class="font-medium text-sqli-midnight mb-3">Description</h2>
            <p class="text-gray-600 whitespace-pre-wrap">{{ job.description }}</p>
          </div>

          <div class="bg-white rounded-xl border border-sqli-gray-100 p-6">
            <h2 class="font-medium text-sqli-midnight mb-3">Required skills</h2>
            <div v-if="job.skills.length" class="flex flex-wrap gap-2">
              <span
                v-for="skill in job.skills"
                :key="skill"
                class="px-2.5 py-1 rounded-full bg-sqli-gray-100 text-sm text-sqli-midnight"
              >
                {{ skill }}
              </span>
            </div>
            <p v-else class="text-gray-400 text-sm">No skills listed</p>
          </div>
        </div>

        <div class="space-y-6">
          <div class="bg-white rounded-xl border border-sqli-gray-100 p-6">
            <h2 class="font-medium text-sqli-midnight mb-4">Pipeline</h2>
            <ul class="space-y-3">
              <li
                v-for="stage in stages"
                :key="stage.id"
                class="flex items-center justify-between text-sm"
              >
                <span class="flex items-center gap-2">
                  <span
                    class="w-2.5 h-2.5 rounded-full shrink-0"
                    :style="{ backgroundColor: stage.color }"
                  />
                  {{ stage.name }}
                </span>
                <span class="text-gray-400">0</span>
              </li>
            </ul>
            <p class="text-xs text-gray-400 mt-4">Candidate counts come in Epic 3</p>
          </div>

          <div class="bg-white rounded-xl border border-sqli-gray-100 p-6 text-sm text-gray-500">
            <p>Created by {{ job.created_by_name ?? '—' }}</p>
            <p class="mt-1">{{ new Date(job.created_at).toLocaleDateString() }}</p>
          </div>
        </div>
      </div>
    </template>

    <AppToast :message="toast" />
  </AppLayout>
</template>
