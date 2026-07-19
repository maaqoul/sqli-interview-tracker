<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import {
  fetchCandidate,
  fetchCandidateTimeline,
  moveCandidateStage,
  uploadCandidateResume,
} from '@/api/candidates'
import { fetchInterviews } from '@/api/interviews'
import { fetchJobStages } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import AppToast from '@/components/AppToast.vue'
import CandidateStageBadge from '@/components/CandidateStageBadge.vue'
import ScheduleInterviewModal from '@/components/ScheduleInterviewModal.vue'
import { useAuthStore } from '@/stores/auth'
import type { Candidate, CandidateActivity } from '@/types/candidates'
import type { Interview } from '@/types/interviews'
import type { PipelineStage } from '@/types/jobs'

type TabId = 'overview' | 'timeline' | 'interviews' | 'scorecards' | 'ai'

const route = useRoute()
const auth = useAuthStore()

const candidate = ref<Candidate | null>(null)
const activities = ref<CandidateActivity[]>([])
const stages = ref<PipelineStage[]>([])
const error = ref('')
const loading = ref(true)
const toast = ref('')
const activeTab = ref<TabId>('overview')

const showMoveModal = ref(false)
const moveStageId = ref<number | ''>('')
const moveReason = ref('')
const moveLoading = ref(false)
const moveError = ref('')

const resumeInput = ref<HTMLInputElement | null>(null)
const resumeUploading = ref(false)
const showScheduleModal = ref(false)
const candidateInterviews = ref<Interview[]>([])

const canManage = computed(
  () => auth.user?.role === 'recruiter' || auth.user?.role === 'admin',
)

const tabs: { id: TabId; label: string }[] = [
  { id: 'overview', label: 'Overview' },
  { id: 'timeline', label: 'Timeline' },
  { id: 'interviews', label: 'Interviews' },
  { id: 'scorecards', label: 'Scorecards' },
  { id: 'ai', label: 'AI Brief' },
]

const sourceLabels: Record<string, string> = {
  linkedin: 'LinkedIn',
  referral: 'Referral',
  job_board: 'Job board',
  other: 'Other',
  '': '—',
}

const rejectedStage = computed(() => stages.value.find((s) => s.name === 'Rejected'))

const moveOptions = computed(() =>
  stages.value.filter((s) => s.id !== candidate.value?.current_stage),
)

async function loadAll() {
  loading.value = true
  error.value = ''
  const id = Number(route.params.id)
  try {
    candidate.value = await fetchCandidate(id)
    const [timeline, jobStages, interviews] = await Promise.all([
      fetchCandidateTimeline(id),
      fetchJobStages(candidate.value.job),
      fetchInterviews({ candidate_id: id }),
    ])
    activities.value = timeline
    stages.value = jobStages
    candidateInterviews.value = interviews.results
  } catch {
    error.value = 'Candidate not found.'
    candidate.value = null
  } finally {
    loading.value = false
  }
}

function showToast(message: string) {
  toast.value = message
  setTimeout(() => {
    toast.value = ''
  }, 3000)
}

function formatWhen(iso: string) {
  return new Date(iso).toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function userLabel(activity: CandidateActivity) {
  if (!activity.user) return 'System'
  return `${activity.user.first_name} ${activity.user.last_name}`.trim() || activity.user.email
}

function openMoveModal(preselectRejected = false) {
  moveError.value = ''
  moveReason.value = ''
  if (preselectRejected && rejectedStage.value) {
    moveStageId.value = rejectedStage.value.id
  } else {
    moveStageId.value = moveOptions.value[0]?.id ?? ''
  }
  showMoveModal.value = true
}

async function submitMove() {
  if (!candidate.value || moveStageId.value === '' || !moveReason.value.trim()) {
    moveError.value = 'Stage and reason are required.'
    return
  }
  moveLoading.value = true
  moveError.value = ''
  try {
    candidate.value = await moveCandidateStage(candidate.value.id, {
      stage_id: Number(moveStageId.value),
      reason: moveReason.value.trim(),
    })
    activities.value = await fetchCandidateTimeline(candidate.value.id)
    showMoveModal.value = false
    showToast('Stage updated.')
  } catch {
    moveError.value = 'Could not move candidate.'
  } finally {
    moveLoading.value = false
  }
}

function onScheduleClick() {
  showScheduleModal.value = true
}

async function onInterviewScheduled() {
  showToast('Interview scheduled.')
  await loadAll()
}

function onAddNoteClick() {
  showToast('Notes API is not available yet — coming later.')
}

async function onResumeSelected(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file || !candidate.value) return

  resumeUploading.value = true
  try {
    candidate.value = await uploadCandidateResume(candidate.value.id, file)
    showToast('Resume uploaded.')
  } catch {
    showToast('Resume upload failed. PDF only, max 5MB.')
  } finally {
    resumeUploading.value = false
    input.value = ''
  }
}

watch(
  () => route.params.id,
  () => {
    activeTab.value = 'overview'
    loadAll()
  },
)

onMounted(loadAll)
</script>

<template>
  <AppLayout>
    <router-link to="/candidates" class="text-sm text-sqli-cobalt hover:underline mb-4 inline-block">
      ← Back to Candidates
    </router-link>

    <div v-if="loading" class="text-gray-500">Loading…</div>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>

    <div v-else-if="candidate">
      <!-- Header -->
      <div class="flex flex-wrap items-start justify-between gap-4 mb-6">
        <div>
          <h1 class="text-2xl font-semibold text-sqli-midnight">
            {{ candidate.first_name }} {{ candidate.last_name }}
          </h1>
          <p class="text-gray-600 text-sm mt-1">
            {{ candidate.email }}
            <span v-if="candidate.phone"> · {{ candidate.phone }}</span>
          </p>
          <p class="text-gray-500 text-sm mt-1">{{ candidate.job_title }}</p>
          <div class="mt-2">
            <CandidateStageBadge
              :name="candidate.current_stage_name"
              :color="candidate.current_stage_color"
            />
          </div>
        </div>

        <div v-if="canManage" class="flex flex-wrap gap-2">
          <button
            type="button"
            class="px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm text-gray-700 hover:bg-sqli-cream"
            @click="onScheduleClick"
          >
            Schedule Interview
          </button>
          <button
            type="button"
            class="px-3 py-2 rounded-lg border border-gray-200 bg-white text-sm text-gray-700 hover:bg-sqli-cream"
            @click="openMoveModal(false)"
          >
            Move Stage
          </button>
          <button
            type="button"
            class="px-3 py-2 rounded-lg bg-red-600 hover:bg-red-700 text-white text-sm font-medium"
            @click="openMoveModal(true)"
          >
            Reject
          </button>
        </div>
      </div>

      <!-- Tabs -->
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

      <!-- Overview -->
      <div
        v-if="activeTab === 'overview'"
        class="bg-white rounded-xl border border-sqli-gray-100 p-6 text-sm"
      >
        <dl class="space-y-3 text-gray-600">
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-400">LinkedIn</dt>
            <dd>
              <a
                v-if="candidate.linkedin"
                :href="candidate.linkedin"
                class="text-sqli-cobalt hover:underline"
                target="_blank"
                rel="noopener"
              >
                {{ candidate.linkedin }}
              </a>
              <span v-else>—</span>
            </dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-400">Source</dt>
            <dd>{{ sourceLabels[candidate.source] ?? '—' }}</dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-400">Status</dt>
            <dd class="capitalize">{{ candidate.status }}</dd>
          </div>
          <div>
            <dt class="text-xs uppercase tracking-wide text-gray-400 mb-1">Resume</dt>
            <dd class="flex flex-wrap items-center gap-3">
              <a
                v-if="candidate.resume_file"
                :href="candidate.resume_file"
                class="text-sqli-cobalt hover:underline"
                target="_blank"
                rel="noopener"
              >
                Download / preview PDF
              </a>
              <span v-else class="text-gray-400">No resume uploaded</span>
              <template v-if="canManage">
                <input
                  ref="resumeInput"
                  type="file"
                  accept="application/pdf,.pdf"
                  class="hidden"
                  @change="onResumeSelected"
                />
                <button
                  type="button"
                  class="text-sm text-sqli-cobalt hover:underline"
                  :disabled="resumeUploading"
                  @click="resumeInput?.click()"
                >
                  {{ resumeUploading ? 'Uploading…' : candidate.resume_file ? 'Replace PDF' : 'Upload PDF' }}
                </button>
              </template>
            </dd>
          </div>
        </dl>

        <div v-if="canManage" class="mt-6 pt-4 border-t border-sqli-gray-100 flex flex-wrap gap-2">
          <button
            type="button"
            class="px-3 py-2 rounded-lg bg-sqli-cobalt text-white text-sm hover:bg-[#003399]"
            @click="openMoveModal(false)"
          >
            Move to next stage
          </button>
          <button
            type="button"
            class="px-3 py-2 rounded-lg border border-gray-200 text-sm text-gray-700 hover:bg-sqli-cream"
            @click="onAddNoteClick"
          >
            Add note
          </button>
        </div>
      </div>

      <!-- Timeline -->
      <div
        v-else-if="activeTab === 'timeline'"
        class="bg-white rounded-xl border border-sqli-gray-100 p-6"
      >
        <ol v-if="activities.length" class="relative border-l border-sqli-gray-100 ml-2 space-y-6">
          <li v-for="event in activities" :key="event.id" class="ml-4">
            <span
              class="absolute -left-1.5 mt-1.5 w-3 h-3 rounded-full border-2 border-white"
              :style="{
                backgroundColor:
                  event.action_type === 'stage_change' ? '#0047BB' : '#6B7280',
              }"
            />
            <p class="text-xs text-gray-400">{{ formatWhen(event.created_at) }}</p>
            <p class="text-sm text-sqli-midnight font-medium mt-0.5">{{ event.description }}</p>
            <p class="text-xs text-gray-500 mt-0.5">by {{ userLabel(event) }}</p>
            <p
              v-if="event.metadata?.reason"
              class="text-xs text-gray-500 mt-1 italic"
            >
              Reason: {{ event.metadata.reason }}
            </p>
          </li>
        </ol>
        <p v-else class="text-sm text-gray-500">No activity yet.</p>
      </div>

      <!-- Interviews -->
      <div
        v-else-if="activeTab === 'interviews'"
        class="bg-white rounded-xl border border-sqli-gray-100 p-6"
      >
        <div v-if="candidateInterviews.length" class="space-y-3">
          <div
            v-for="iv in candidateInterviews"
            :key="iv.id"
            class="border border-sqli-gray-100 rounded-lg p-3 text-sm"
          >
            <p class="font-medium text-sqli-midnight capitalize">
              {{ iv.type }} · {{ new Date(iv.scheduled_at).toLocaleString('en-GB') }}
            </p>
            <p class="text-gray-500 text-xs mt-0.5">
              {{ iv.duration_min }} min · {{ iv.status }} ·
              {{ iv.interviewer_names.join(', ') || 'No interviewers' }}
            </p>
          </div>
        </div>
        <div v-else class="text-center py-4">
          <p class="text-sqli-midnight font-medium">No interviews yet</p>
          <p class="text-sm text-gray-500 mt-1">Schedule one from the button above.</p>
        </div>
        <button
          v-if="canManage"
          type="button"
          class="mt-4 px-4 py-2 rounded-lg bg-sqli-cobalt text-white text-sm"
          @click="onScheduleClick"
        >
          Schedule Interview
        </button>
      </div>

      <!-- Scorecards (aggregate in INT-033) -->
      <div
        v-else-if="activeTab === 'scorecards'"
        class="bg-white rounded-xl border border-sqli-gray-100 p-8 text-center"
      >
        <p class="text-sqli-midnight font-medium">Scorecards</p>
        <p class="text-sm text-gray-500 mt-1">
          Aggregated scorecard view comes in INT-033. Interviewers submit via My Interviews.
        </p>
      </div>

      <!-- AI Brief (placeholder until INT-036) -->
      <div
        v-else-if="activeTab === 'ai'"
        class="bg-white rounded-xl border border-sqli-gray-100 p-6"
      >
        <p class="text-xs uppercase tracking-wide text-amber-700 mb-2">
          Generated by AI — human decision required
        </p>
        <p class="text-sqli-midnight font-medium">AI Hiring Brief</p>
        <p class="text-sm text-gray-500 mt-2">
          This tab will show an AI summary of scorecards and notes (INT-036).
        </p>
        <button
          type="button"
          class="mt-4 px-4 py-2 rounded-lg border border-gray-200 text-sm text-gray-500 cursor-not-allowed"
          disabled
        >
          Regenerate Brief
        </button>
      </div>
    </div>

    <!-- Move / Reject modal -->
    <div
      v-if="showMoveModal"
      class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
      @click.self="showMoveModal = false"
    >
      <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
        <h2 class="text-lg font-semibold text-sqli-midnight mb-4">Move candidate</h2>
        <label class="block mb-3">
          <span class="text-sm text-gray-600">Stage</span>
          <select
            v-model="moveStageId"
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white text-sm"
          >
            <option v-for="stage in moveOptions" :key="stage.id" :value="stage.id">
              {{ stage.name }}
            </option>
          </select>
        </label>
        <label class="block mb-4">
          <span class="text-sm text-gray-600">Reason</span>
          <textarea
            v-model="moveReason"
            rows="3"
            required
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 text-sm"
            placeholder="Why is this move happening?"
          />
        </label>
        <p v-if="moveError" class="text-red-500 text-sm mb-3">{{ moveError }}</p>
        <div class="flex justify-end gap-2">
          <button
            type="button"
            class="px-4 py-2 rounded-lg border border-gray-200 text-sm"
            @click="showMoveModal = false"
          >
            Cancel
          </button>
          <button
            type="button"
            class="px-4 py-2 rounded-lg bg-sqli-cobalt text-white text-sm disabled:opacity-50"
            :disabled="moveLoading"
            @click="submitMove"
          >
            {{ moveLoading ? 'Saving…' : 'Confirm' }}
          </button>
        </div>
      </div>
    </div>

    <ScheduleInterviewModal
      :open="showScheduleModal"
      :prefill-candidate-id="candidate?.id"
      @close="showScheduleModal = false"
      @saved="onInterviewScheduled"
    />

    <AppToast :message="toast" />
  </AppLayout>
</template>
