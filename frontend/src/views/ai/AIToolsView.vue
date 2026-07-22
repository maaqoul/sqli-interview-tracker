<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { generateQuestions } from '@/api/ai'
import { fetchJobs } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import AppToast from '@/components/AppToast.vue'
import type { InterviewQuestion } from '@/types/ai'
import type { Job } from '@/types/jobs'

type TabId = 'questions' | 'mock' | 'history'

const activeTab = ref<TabId>('questions')
const jobs = ref<Job[]>([])
const selectedJobId = ref<number | ''>('')
const level = ref('mid')
const interviewType = ref('technical')
const questions = ref<InterviewQuestion[]>([])
const loading = ref(false)
const error = ref('')
const toast = ref('')
const pageLoading = ref(true)

const selectedJob = computed(() =>
  jobs.value.find((j) => j.id === selectedJobId.value) ?? null,
)

const tabs: { id: TabId; label: string }[] = [
  { id: 'questions', label: 'Question Generator' },
  { id: 'mock', label: 'Mock Interview' },
  { id: 'history', label: 'History' },
]

const levels = [
  { value: 'junior', label: 'Junior' },
  { value: 'mid', label: 'Mid' },
  { value: 'senior', label: 'Senior' },
  { value: 'lead', label: 'Lead' },
]

const interviewTypes = [
  { value: 'technical', label: 'Technical' },
  { value: 'behavioral', label: 'Behavioral' },
  { value: 'mixed', label: 'Mixed' },
]

const difficultyClass: Record<string, string> = {
  easy: 'bg-green-50 text-green-700',
  medium: 'bg-amber-50 text-amber-800',
  hard: 'bg-red-50 text-red-700',
}

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => {
    toast.value = ''
  }, 2500)
}

watch(selectedJob, (job) => {
  if (job) level.value = job.level
})

async function loadJobs() {
  pageLoading.value = true
  try {
    const data = await fetchJobs('open')
    jobs.value = data.results
    if (jobs.value.length && selectedJobId.value === '') {
      selectedJobId.value = jobs.value[0].id
    }
  } catch {
    error.value = 'Could not load jobs.'
  } finally {
    pageLoading.value = false
  }
}

async function runGenerate() {
  error.value = ''
  const job = selectedJob.value
  const title = job?.title?.trim()
  if (!title) {
    error.value = 'Select a job first.'
    return
  }

  loading.value = true
  try {
    const data = await generateQuestions({
      job_id: job?.id ?? null,
      job_title: title,
      level: level.value,
      skills: job?.skills ?? [],
      interview_type: interviewType.value,
      n: 10,
      save: true,
    })
    questions.value = data.questions
    showToast(`Generated ${data.count} questions.`)
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const detail = err.response?.data?.detail
      error.value =
        typeof detail === 'string'
          ? detail
          : err.response?.status === 429
            ? 'AI rate limit reached (20/hour). Try again later.'
            : 'Generation failed.'
    } else {
      error.value = 'Generation failed.'
    }
  } finally {
    loading.value = false
  }
}

async function copyAll() {
  if (!questions.value.length) return
  const text = questions.value
    .map(
      (q, i) =>
        `${i + 1}. [${q.type} · ${q.difficulty}] ${q.question}`,
    )
    .join('\n')
  try {
    await navigator.clipboard.writeText(text)
    showToast('Copied to clipboard.')
  } catch {
    showToast('Could not copy.')
  }
}

onMounted(loadJobs)
</script>

<template>
  <AppLayout>
    <div class="mb-6">
      <h1 class="text-2xl font-semibold text-sqli-midnight">AI Interview Assistant</h1>
      <p class="text-gray-500 text-sm mt-1">
        Generate questions, practice interviews, and review past AI sessions
      </p>
    </div>

    <div class="border-b border-sqli-gray-100 mb-6 flex gap-1 overflow-x-auto">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        class="px-4 py-2.5 text-sm font-medium border-b-2 -mb-px transition-colors whitespace-nowrap"
        :class="
          activeTab === tab.id
            ? 'border-sqli-cobalt text-sqli-cobalt'
            : 'border-transparent text-gray-500 hover:text-sqli-midnight'
        "
        @click="activeTab = tab.id"
      >
        {{ tab.label }}
      </button>
    </div>

    <!-- Question Generator -->
    <div v-if="activeTab === 'questions'" class="space-y-6 max-w-3xl">
      <div v-if="pageLoading" class="text-sm text-gray-500">Loading jobs…</div>

      <div v-else class="bg-white rounded-xl border border-sqli-gray-100 p-6 space-y-4">
        <div>
          <label class="text-sm font-medium text-sqli-midnight" for="job">Job</label>
          <select
            id="job"
            v-model="selectedJobId"
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white text-sm focus:outline-none focus:ring-2 focus:ring-sqli-sky"
          >
            <option disabled value="">Select a job…</option>
            <option v-for="job in jobs" :key="job.id" :value="job.id">
              {{ job.title }}
            </option>
          </select>
          <p v-if="selectedJob?.skills?.length" class="text-xs text-gray-400 mt-1">
            Skills: {{ selectedJob.skills.join(', ') }}
          </p>
        </div>

        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="text-sm font-medium text-sqli-midnight" for="level">Level</label>
            <select
              id="level"
              v-model="level"
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white text-sm"
            >
              <option v-for="opt in levels" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="text-sm font-medium text-sqli-midnight" for="itype">Type</label>
            <select
              id="itype"
              v-model="interviewType"
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white text-sm"
            >
              <option v-for="opt in interviewTypes" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </div>

        <button
          type="button"
          class="bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-5 py-2.5 rounded-lg disabled:opacity-50 inline-flex items-center gap-2"
          :disabled="loading || !selectedJobId"
          @click="runGenerate"
        >
          <span
            v-if="loading"
            class="inline-block w-4 h-4 border-2 border-white/40 border-t-white rounded-full animate-spin"
          />
          {{ loading ? 'Generating…' : 'Generate Questions' }}
        </button>
        <p v-if="loading" class="text-xs text-gray-400">
          This can take up to ~10 seconds with a live AI provider.
        </p>
        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
      </div>

      <div
        v-if="questions.length"
        class="bg-white rounded-xl border border-sqli-gray-100 p-6"
      >
        <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
          <h2 class="text-lg font-semibold text-sqli-midnight">
            Generated Questions
            <span class="text-sm font-normal text-gray-400">({{ questions.length }})</span>
          </h2>
          <div class="flex flex-wrap gap-2">
            <button
              type="button"
              class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm"
              @click="copyAll"
            >
              Copy All
            </button>
            <button
              type="button"
              class="px-3 py-1.5 rounded-lg border border-gray-200 text-sm"
              :disabled="loading"
              @click="runGenerate"
            >
              Regenerate
            </button>
          </div>
        </div>

        <ol class="space-y-3">
          <li
            v-for="(q, i) in questions"
            :key="i"
            class="border border-sqli-gray-100 rounded-lg p-3 text-sm"
          >
            <div class="flex flex-wrap gap-2 mb-1.5">
              <span class="text-xs px-2 py-0.5 rounded-md bg-sqli-cream text-sqli-midnight capitalize">
                {{ q.type }}
              </span>
              <span
                class="text-xs px-2 py-0.5 rounded-md capitalize"
                :class="difficultyClass[q.difficulty] || 'bg-gray-50 text-gray-600'"
              >
                {{ q.difficulty }}
              </span>
            </div>
            <p class="text-sqli-midnight">
              <span class="text-gray-400 mr-1">{{ i + 1 }}.</span>
              {{ q.question }}
            </p>
          </li>
        </ol>
      </div>
    </div>

    <!-- Placeholders for later tickets -->
    <div
      v-else-if="activeTab === 'mock'"
      class="bg-white rounded-xl border border-sqli-gray-100 p-8 text-center max-w-3xl"
    >
      <p class="text-sqli-midnight font-medium">Mock Interview</p>
      <p class="text-sm text-gray-500 mt-1">Coming in INT-037.</p>
    </div>

    <div
      v-else
      class="bg-white rounded-xl border border-sqli-gray-100 p-8 text-center max-w-3xl"
    >
      <p class="text-sqli-midnight font-medium">AI session history</p>
      <p class="text-sm text-gray-500 mt-1">Coming in INT-038.</p>
    </div>

    <AppToast :message="toast" />
  </AppLayout>
</template>
