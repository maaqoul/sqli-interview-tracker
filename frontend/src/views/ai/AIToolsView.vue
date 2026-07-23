<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref, watch } from 'vue'
import { fetchAISession, fetchAISessions, generateQuestions, mockInterviewTurn } from '@/api/ai'
import { fetchJobs } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import AppToast from '@/components/AppToast.vue'
import type { AISession, AISessionType, ChatMessage, InterviewQuestion } from '@/types/ai'
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

// Mock interview state
const mockRole = ref('')
const mockLevel = ref('mid')
const mockHistory = ref<ChatMessage[]>([])
const mockSessionId = ref<number | null>(null)
const mockAnswer = ref('')
const mockLoading = ref(false)
const mockError = ref('')
const mockDone = ref(false)
const mockSummary = ref('')
const mockStarted = ref(false)

// History state
const historyFilter = ref<AISessionType | ''>('')
const sessions = ref<AISession[]>([])
const historyLoading = ref(false)
const historyError = ref('')
const selectedSession = ref<AISession | null>(null)
const detailLoading = ref(false)

const selectedJob = computed(() =>
  jobs.value.find((j) => j.id === selectedJobId.value) ?? null,
)

const selectedTranscript = computed(() => {
  const out = selectedSession.value?.output_data as
    | {
        history?: ChatMessage[]
        questions?: InterviewQuestion[]
        summary?: string
        recommendation?: string
        suggested_next_step?: string
      }
    | undefined
  return out
})

const selectedQuestions = computed(
  () => selectedTranscript.value?.questions ?? [],
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
  if (job) {
    level.value = job.level
    if (!mockRole.value) mockRole.value = job.title
    mockLevel.value = job.level
  }
})

async function loadJobs() {
  pageLoading.value = true
  try {
    const data = await fetchJobs('open')
    jobs.value = data.results
    if (jobs.value.length && selectedJobId.value === '') {
      selectedJobId.value = jobs.value[0].id
      mockRole.value = jobs.value[0].title
      mockLevel.value = jobs.value[0].level
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

async function startMock() {
  mockError.value = ''
  if (!mockRole.value.trim()) {
    mockError.value = 'Enter a role first.'
    return
  }
  mockLoading.value = true
  mockDone.value = false
  mockSummary.value = ''
  mockHistory.value = []
  mockSessionId.value = null
  try {
    const data = await mockInterviewTurn({
      role: mockRole.value.trim(),
      level: mockLevel.value,
      history: [],
      user_answer: '',
    })
    mockHistory.value = data.history
    mockSessionId.value = data.session_id
    mockStarted.value = true
    mockDone.value = data.done
  } catch (err) {
    mockError.value = axios.isAxiosError(err)
      ? String(err.response?.data?.detail || 'Could not start mock interview.')
      : 'Could not start mock interview.'
  } finally {
    mockLoading.value = false
  }
}

async function sendMockAnswer() {
  if (!mockAnswer.value.trim() || mockDone.value) return
  mockLoading.value = true
  mockError.value = ''
  const answer = mockAnswer.value.trim()
  mockAnswer.value = ''
  try {
    const data = await mockInterviewTurn({
      role: mockRole.value.trim(),
      level: mockLevel.value,
      history: mockHistory.value,
      user_answer: answer,
      session_id: mockSessionId.value,
    })
    mockHistory.value = data.history
    mockSessionId.value = data.session_id
    mockDone.value = data.done
    if (data.done) mockSummary.value = data.summary
  } catch (err) {
    mockError.value = axios.isAxiosError(err)
      ? String(err.response?.data?.detail || 'Could not send answer.')
      : 'Could not send answer.'
  } finally {
    mockLoading.value = false
  }
}

async function endMock() {
  mockLoading.value = true
  mockError.value = ''
  try {
    const data = await mockInterviewTurn({
      role: mockRole.value.trim(),
      level: mockLevel.value,
      history: mockHistory.value,
      user_answer: '',
      session_id: mockSessionId.value,
      end: true,
    })
    mockHistory.value = data.history
    mockDone.value = true
    mockSummary.value = data.summary
  } catch (err) {
    mockError.value = axios.isAxiosError(err)
      ? String(err.response?.data?.detail || 'Could not end session.')
      : 'Could not end session.'
  } finally {
    mockLoading.value = false
  }
}

function resetMock() {
  mockStarted.value = false
  mockHistory.value = []
  mockSessionId.value = null
  mockAnswer.value = ''
  mockDone.value = false
  mockSummary.value = ''
  mockError.value = ''
}

async function loadSessions() {
  historyLoading.value = true
  historyError.value = ''
  try {
    const data = await fetchAISessions(historyFilter.value)
    sessions.value = data.results
  } catch {
    historyError.value = 'Could not load sessions.'
    sessions.value = []
  } finally {
    historyLoading.value = false
  }
}

async function openSession(id: number) {
  detailLoading.value = true
  try {
    selectedSession.value = await fetchAISession(id)
  } catch {
    historyError.value = 'Could not load session detail.'
    selectedSession.value = null
  } finally {
    detailLoading.value = false
  }
}

function closeSessionDetail() {
  selectedSession.value = null
}

function formatSessionWhen(iso: string) {
  return new Date(iso).toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

const typeLabel: Record<AISessionType, string> = {
  questions: 'Questions',
  summary: 'Summary',
  mock: 'Mock',
}

watch(activeTab, (tab) => {
  if (tab === 'history') {
    selectedSession.value = null
    loadSessions()
  }
})

watch(historyFilter, () => {
  if (activeTab.value === 'history') {
    selectedSession.value = null
    loadSessions()
  }
})

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

    <!-- Mock Interview -->
    <div v-else-if="activeTab === 'mock'" class="space-y-4 max-w-3xl">
      <div class="bg-white rounded-xl border border-sqli-gray-100 p-6 space-y-4">
        <div class="grid sm:grid-cols-2 gap-4">
          <div>
            <label class="text-sm font-medium text-sqli-midnight" for="mock-role">Role</label>
            <input
              id="mock-role"
              v-model="mockRole"
              type="text"
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
              :disabled="mockStarted"
              placeholder="e.g. Senior Python Developer"
            />
          </div>
          <div>
            <label class="text-sm font-medium text-sqli-midnight" for="mock-level">Level</label>
            <select
              id="mock-level"
              v-model="mockLevel"
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm bg-white"
              :disabled="mockStarted"
            >
              <option v-for="opt in levels" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
        </div>
        <div class="flex flex-wrap gap-2">
          <button
            v-if="!mockStarted"
            type="button"
            class="bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-4 py-2 rounded-lg disabled:opacity-50"
            :disabled="mockLoading"
            @click="startMock"
          >
            {{ mockLoading ? 'Starting…' : 'Start Session' }}
          </button>
          <template v-else>
            <button
              v-if="!mockDone"
              type="button"
              class="px-4 py-2 rounded-lg border border-gray-200 text-sm"
              :disabled="mockLoading"
              @click="endMock"
            >
              End session
            </button>
            <button
              type="button"
              class="px-4 py-2 rounded-lg border border-gray-200 text-sm"
              @click="resetMock"
            >
              New session
            </button>
          </template>
        </div>
        <p v-if="mockError" class="text-sm text-red-600">{{ mockError }}</p>
      </div>

      <div
        v-if="mockStarted"
        class="bg-white rounded-xl border border-sqli-gray-100 p-4 min-h-[280px] flex flex-col"
      >
        <div class="flex-1 space-y-3 overflow-y-auto max-h-[420px] mb-4">
          <div
            v-for="(msg, i) in mockHistory"
            :key="i"
            class="flex"
            :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
          >
            <div
              class="max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm whitespace-pre-wrap"
              :class="
                msg.role === 'user'
                  ? 'bg-sqli-cobalt text-white rounded-br-md'
                  : 'bg-sqli-cream text-sqli-midnight rounded-bl-md'
              "
            >
              <span v-if="msg.role === 'assistant'" class="text-xs text-sqli-cobalt block mb-1">
                SQLI Interviewer
              </span>
              {{ msg.content }}
            </div>
          </div>
        </div>

        <div
          v-if="mockDone && mockSummary"
          class="mb-3 rounded-lg border border-amber-200 bg-amber-50 p-3 text-sm text-amber-900"
        >
          <p class="font-medium mb-1">Session summary</p>
          <p>{{ mockSummary }}</p>
        </div>

        <form
          v-if="!mockDone"
          class="flex gap-2"
          @submit.prevent="sendMockAnswer"
        >
          <input
            v-model="mockAnswer"
            type="text"
            class="flex-1 rounded-lg border border-gray-200 px-3 py-2 text-sm"
            placeholder="Type your answer…"
            :disabled="mockLoading"
          />
          <button
            type="submit"
            class="bg-sqli-cobalt text-white px-4 py-2 rounded-lg text-sm disabled:opacity-50"
            :disabled="mockLoading || !mockAnswer.trim()"
          >
            Send
          </button>
        </form>
      </div>
    </div>

    <!-- History -->
    <div v-else class="space-y-4 max-w-3xl">
      <div class="flex flex-wrap gap-2">
        <button
          v-for="opt in [
            { value: '', label: 'All' },
            { value: 'questions', label: 'Questions' },
            { value: 'summary', label: 'Summary' },
            { value: 'mock', label: 'Mock' },
          ]"
          :key="opt.value || 'all'"
          type="button"
          class="px-3 py-1.5 rounded-lg border text-sm transition-colors"
          :class="
            historyFilter === opt.value
              ? 'border-sqli-cobalt bg-sqli-cobalt text-white'
              : 'border-gray-200 text-gray-600 hover:border-sqli-sky'
          "
          @click="historyFilter = opt.value as typeof historyFilter"
        >
          {{ opt.label }}
        </button>
      </div>

      <div v-if="historyLoading" class="text-sm text-gray-500">Loading sessions…</div>
      <p v-else-if="historyError" class="text-sm text-red-600">{{ historyError }}</p>

      <div
        v-else-if="!sessions.length"
        class="bg-white rounded-xl border border-sqli-gray-100 p-8 text-center"
      >
        <p class="text-sqli-midnight font-medium">No sessions yet</p>
        <p class="text-sm text-gray-500 mt-1">
          Generate questions, create a hiring brief, or run a mock interview.
        </p>
      </div>

      <div v-else class="space-y-2">
        <button
          v-for="s in sessions"
          :key="s.id"
          type="button"
          class="w-full text-left bg-white rounded-xl border border-sqli-gray-100 p-4 hover:border-sqli-sky transition-colors"
          @click="openSession(s.id)"
        >
          <div class="flex flex-wrap items-center justify-between gap-2">
            <span
              class="text-xs px-2 py-0.5 rounded-md bg-sqli-cream text-sqli-midnight capitalize"
            >
              {{ typeLabel[s.type] }}
            </span>
            <span class="text-xs text-gray-400">{{ formatSessionWhen(s.created_at) }}</span>
          </div>
          <p class="text-sm text-sqli-midnight mt-1.5">{{ s.preview }}</p>
        </button>
      </div>

      <!-- Detail panel -->
      <div
        v-if="selectedSession || detailLoading"
        class="bg-white rounded-xl border border-sqli-gray-100 p-5"
      >
        <div class="flex items-center justify-between mb-3">
          <h3 class="font-medium text-sqli-midnight">Session detail</h3>
          <button
            type="button"
            class="text-sm text-gray-500 hover:text-sqli-midnight"
            @click="closeSessionDetail"
          >
            Close
          </button>
        </div>
        <div v-if="detailLoading" class="text-sm text-gray-500">Loading…</div>
        <template v-else-if="selectedSession">
          <p class="text-xs text-gray-400 mb-3">
            {{ typeLabel[selectedSession.type] }} ·
            {{ formatSessionWhen(selectedSession.created_at) }}
          </p>

          <!-- Mock transcript -->
          <div v-if="selectedSession.type === 'mock'" class="space-y-3">
            <div
              v-for="(msg, i) in selectedTranscript?.history || []"
              :key="i"
              class="flex"
              :class="msg.role === 'user' ? 'justify-end' : 'justify-start'"
            >
              <div
                class="max-w-[85%] rounded-2xl px-3.5 py-2.5 text-sm whitespace-pre-wrap"
                :class="
                  msg.role === 'user'
                    ? 'bg-sqli-cobalt text-white rounded-br-md'
                    : 'bg-sqli-cream text-sqli-midnight rounded-bl-md'
                "
              >
                {{ msg.content }}
              </div>
            </div>
            <p
              v-if="selectedTranscript?.summary"
              class="text-sm text-amber-900 bg-amber-50 border border-amber-200 rounded-lg p-3"
            >
              {{ selectedTranscript.summary }}
            </p>
            <p
              v-if="!(selectedTranscript?.history || []).length"
              class="text-sm text-gray-500"
            >
              No transcript messages saved.
            </p>
          </div>

          <!-- Questions list -->
          <ol
            v-else-if="selectedSession.type === 'questions'"
            class="space-y-2 text-sm"
          >
            <li
              v-for="(q, i) in selectedQuestions"
              :key="i"
              class="border border-sqli-gray-100 rounded-lg p-3"
            >
              <span class="text-gray-400 mr-1">{{ i + 1 }}.</span>
              {{ q.question }}
              <span class="text-xs text-gray-400 ml-1 capitalize">
                ({{ q.type }} · {{ q.difficulty }})
              </span>
            </li>
          </ol>

          <!-- Summary brief -->
          <div v-else class="text-sm space-y-2 text-gray-700">
            <p>
              <span class="text-gray-400 text-xs uppercase">Recommendation</span><br />
              {{ selectedTranscript?.recommendation || '—' }}
            </p>
            <p>
              <span class="text-gray-400 text-xs uppercase">Next step</span><br />
              {{ selectedTranscript?.suggested_next_step || '—' }}
            </p>
            <div v-if="selectedSession.candidate_name">
              <span class="text-gray-400 text-xs uppercase">Candidate</span><br />
              {{ selectedSession.candidate_name }}
            </div>
          </div>
        </template>
      </div>
    </div>

    <AppToast :message="toast" />
  </AppLayout>
</template>
