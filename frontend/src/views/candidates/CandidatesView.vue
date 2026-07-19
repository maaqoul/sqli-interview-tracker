<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { fetchCandidates } from '@/api/candidates'
import { fetchJobs, fetchJobStages } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import AppToast from '@/components/AppToast.vue'
import CandidatesKanban from '@/components/CandidatesKanban.vue'
import CandidatesTable from '@/components/CandidatesTable.vue'
import { useAuthStore } from '@/stores/auth'
import type { Candidate } from '@/types/candidates'
import type { Job, PipelineStage } from '@/types/jobs'

const router = useRouter()
const auth = useAuthStore()

const viewMode = ref<'table' | 'kanban'>('table')
const candidates = ref<Candidate[]>([])
const jobs = ref<Job[]>([])
const stages = ref<PipelineStage[]>([])
const loading = ref(true)
const error = ref('')
const toast = ref('')

const search = ref('')
const jobFilter = ref<number | ''>('')
const stageFilter = ref<number | ''>('')
const page = ref(1)
const totalCount = ref(0)
const sortKey = ref('date')
const sortDir = ref<'asc' | 'desc'>('desc')

let searchTimer: ReturnType<typeof setTimeout> | null = null

const canManage = computed(
  () => auth.user?.role === 'recruiter' || auth.user?.role === 'admin',
)

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / 20)))

const stageOptions = computed(() => {
  if (jobFilter.value) return stages.value
  return []
})

async function loadJobs() {
  const data = await fetchJobs()
  jobs.value = data.results
}

async function loadStagesForJob(jobId: number) {
  stages.value = await fetchJobStages(jobId)
}

async function loadCandidates() {
  loading.value = true
  error.value = ''
  try {
    if (viewMode.value === 'kanban' && jobFilter.value) {
      candidates.value = await fetchAllForJob(Number(jobFilter.value))
      totalCount.value = candidates.value.length
    } else {
      const data = await fetchCandidates({
        job_id: jobFilter.value ? Number(jobFilter.value) : undefined,
        stage: stageFilter.value ? Number(stageFilter.value) : undefined,
        search: search.value.trim() || undefined,
        page: page.value,
      })
      candidates.value = data.results
      totalCount.value = data.count
    }
  } catch {
    error.value = 'Could not load candidates. Is the backend running?'
  } finally {
    loading.value = false
  }
}

async function fetchAllForJob(jobId: number) {
  const first = await fetchCandidates({
    job_id: jobId,
    search: search.value.trim() || undefined,
    page: 1,
  })
  let results = [...first.results]
  let pageNum = 2
  while (results.length < first.count) {
    const next = await fetchCandidates({
      job_id: jobId,
      search: search.value.trim() || undefined,
      page: pageNum,
    })
    results = results.concat(next.results)
    pageNum += 1
    if (!next.next) break
  }
  return results
}

function onSearchInput() {
  if (searchTimer) clearTimeout(searchTimer)
  searchTimer = setTimeout(() => {
    page.value = 1
    loadCandidates()
  }, 300)
}

function onSort(key: string) {
  if (sortKey.value === key) {
    sortDir.value = sortDir.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortDir.value = 'asc'
  }
}

function showToast(message: string) {
  toast.value = message
  setTimeout(() => {
    toast.value = ''
  }, 3000)
}

watch(jobFilter, async (jobId) => {
  stageFilter.value = ''
  page.value = 1
  if (jobId) {
    try {
      await loadStagesForJob(Number(jobId))
    } catch {
      stages.value = []
    }
  } else {
    stages.value = []
    if (viewMode.value === 'kanban') {
      viewMode.value = 'table'
    }
  }
  loadCandidates()
})

watch(stageFilter, () => {
  page.value = 1
  loadCandidates()
})

watch(viewMode, async (mode) => {
  if (mode === 'kanban' && !jobFilter.value && jobs.value.length > 0) {
    jobFilter.value = jobs.value[0].id
    return
  }
  page.value = 1
  loadCandidates()
})

watch(page, loadCandidates)

onMounted(async () => {
  try {
    await loadJobs()
  } catch {
    error.value = 'Could not load jobs for filters.'
  }
  await loadCandidates()
})
</script>

<template>
  <AppLayout>
    <div class="flex items-center justify-between mb-6 gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-semibold text-sqli-midnight">Candidates</h1>
        <p class="text-gray-500 text-sm mt-1">Track applicants through the hiring pipeline</p>
      </div>
      <div class="flex items-center gap-3">
        <div class="inline-flex rounded-lg border border-gray-200 bg-white p-0.5 text-sm">
          <button
            type="button"
            class="px-3 py-1.5 rounded-md transition-colors"
            :class="viewMode === 'table' ? 'bg-sqli-cobalt text-white' : 'text-gray-600 hover:bg-sqli-cream'"
            @click="viewMode = 'table'"
          >
            Table
          </button>
          <button
            type="button"
            class="px-3 py-1.5 rounded-md transition-colors"
            :class="viewMode === 'kanban' ? 'bg-sqli-cobalt text-white' : 'text-gray-600 hover:bg-sqli-cream'"
            @click="viewMode = 'kanban'"
          >
            Kanban
          </button>
        </div>
        <router-link
          v-if="canManage"
          to="/candidates/new"
          class="bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-4 py-2.5 rounded-lg transition-colors"
        >
          + Add Candidate
        </router-link>
      </div>
    </div>

    <div class="flex flex-wrap gap-3 mb-4">
      <input
        v-model="search"
        type="search"
        placeholder="Search name or email…"
        class="rounded-lg border border-gray-200 px-3 py-2 text-sm bg-white min-w-[200px] focus:outline-none focus:ring-2 focus:ring-sqli-sky"
        @input="onSearchInput"
      />
      <select
        v-model="jobFilter"
        class="rounded-lg border border-gray-200 px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sqli-sky"
      >
        <option value="">All jobs</option>
        <option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.title }}</option>
      </select>
      <select
        v-if="viewMode === 'table'"
        v-model="stageFilter"
        :disabled="!jobFilter"
        class="rounded-lg border border-gray-200 px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-sqli-sky disabled:opacity-50"
      >
        <option value="">All stages</option>
        <option v-for="stage in stageOptions" :key="stage.id" :value="stage.id">
          {{ stage.name }}
        </option>
      </select>
    </div>

    <p v-if="viewMode === 'kanban' && !jobFilter" class="text-amber-700 text-sm mb-4">
      Select a job to use the kanban board (stages are per job).
    </p>

    <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>

    <div
      v-if="loading"
      class="bg-white rounded-xl border border-sqli-gray-100 p-8 text-center text-gray-500"
    >
      Loading candidates…
    </div>

    <div
      v-else-if="candidates.length === 0 && viewMode === 'table'"
      class="bg-white rounded-xl border border-sqli-gray-100 p-12 text-center"
    >
      <p class="text-sqli-midnight font-medium mb-2">No candidates yet</p>
      <p class="text-gray-500 text-sm mb-6">Add someone to a job opening to start the pipeline.</p>
      <router-link
        v-if="canManage"
        to="/candidates/new"
        class="inline-block bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-4 py-2.5 rounded-lg"
      >
        Add Candidate
      </router-link>
    </div>

    <CandidatesTable
      v-else-if="viewMode === 'table'"
      :candidates="candidates"
      :sort-key="sortKey"
      :sort-dir="sortDir"
      @sort="onSort"
      @select="(id) => router.push(`/candidates/${id}`)"
    />

    <CandidatesKanban
      v-else-if="viewMode === 'kanban' && jobFilter"
      :candidates="candidates"
      :stages="stages"
      :can-move="canManage"
      @moved="loadCandidates"
      @error="showToast"
    />

    <div
      v-if="viewMode === 'table' && totalCount > 20"
      class="flex justify-end items-center gap-3 mt-4 text-sm text-gray-600"
    >
      <button
        type="button"
        class="px-3 py-1.5 rounded-lg border border-gray-200 bg-white disabled:opacity-40"
        :disabled="page <= 1"
        @click="page -= 1"
      >
        ← Prev
      </button>
      <span>Page {{ page }} of {{ totalPages }}</span>
      <button
        type="button"
        class="px-3 py-1.5 rounded-lg border border-gray-200 bg-white disabled:opacity-40"
        :disabled="page >= totalPages"
        @click="page += 1"
      >
        Next →
      </button>
    </div>

    <AppToast :message="toast" />
  </AppLayout>
</template>
