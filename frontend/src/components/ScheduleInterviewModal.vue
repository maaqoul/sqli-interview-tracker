<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import axios from 'axios'
import { createInterview, fetchAssignableUsers, updateInterview } from '@/api/interviews'
import { fetchCandidates } from '@/api/candidates'
import type { Candidate } from '@/types/candidates'
import type { Interview, InterviewType } from '@/types/interviews'

const props = defineProps<{
  open: boolean
  prefillCandidateId?: number | null
  editInterview?: Interview | null
}>()

const emit = defineEmits<{
  close: []
  saved: []
}>()

const candidates = ref<Candidate[]>([])
const users = ref<
  { id: number; email: string; first_name: string; last_name: string; role: string }[]
>([])

const candidateId = ref<number | ''>('')
const type = ref<InterviewType>('video')
const date = ref('')
const time = ref('10:00')
const durationMin = ref(60)
const location = ref('')
const videoLink = ref('')
const interviewerIds = ref<number[]>([])
const status = ref<'scheduled' | 'completed' | 'cancelled' | 'no_show'>('scheduled')

const loading = ref(false)
const error = ref('')

const selectedCandidate = computed(() =>
  candidates.value.find((c) => c.id === Number(candidateId.value)),
)

const isEdit = computed(() => Boolean(props.editInterview))

async function loadOptions() {
  const [cands, people] = await Promise.all([
    fetchCandidates({ page: 1 }),
    fetchAssignableUsers(),
  ])
  // Load more candidate pages if needed for select
  let all = [...cands.results]
  let page = 2
  while (all.length < cands.count && page <= 10) {
    const next = await fetchCandidates({ page })
    all = all.concat(next.results)
    page += 1
    if (!next.next) break
  }
  candidates.value = all
  users.value = people.filter((u) =>
    ['interviewer', 'recruiter', 'admin', 'hiring_manager'].includes(u.role),
  )
}

function resetForm() {
  error.value = ''
  type.value = 'video'
  durationMin.value = 60
  location.value = ''
  videoLink.value = ''
  interviewerIds.value = []
  status.value = 'scheduled'

  if (props.editInterview) {
    const iv = props.editInterview
    candidateId.value = iv.candidate
    type.value = iv.type
    const dt = new Date(iv.scheduled_at)
    date.value = dt.toISOString().slice(0, 10)
    time.value = dt.toTimeString().slice(0, 5)
    durationMin.value = iv.duration_min
    location.value = iv.location || ''
    videoLink.value = iv.video_link || ''
    interviewerIds.value = [...iv.interviewer_ids]
    status.value = iv.status
  } else {
    candidateId.value = props.prefillCandidateId ?? ''
    const tomorrow = new Date()
    tomorrow.setDate(tomorrow.getDate() + 1)
    date.value = tomorrow.toISOString().slice(0, 10)
    time.value = '10:00'
  }
}

watch(
  () => props.open,
  async (open) => {
    if (!open) return
    try {
      await loadOptions()
      resetForm()
    } catch {
      error.value = 'Could not load form options.'
    }
  },
)

function toggleInterviewer(id: number) {
  if (interviewerIds.value.includes(id)) {
    interviewerIds.value = interviewerIds.value.filter((x) => x !== id)
  } else {
    interviewerIds.value = [...interviewerIds.value, id]
  }
}

async function submit() {
  if (!candidateId.value || !date.value || !time.value || interviewerIds.value.length === 0) {
    error.value = 'Candidate, date/time, and at least one interviewer are required.'
    return
  }
  const candidate = selectedCandidate.value
  if (!candidate && !props.editInterview) {
    error.value = 'Select a valid candidate.'
    return
  }

  const scheduledAt = new Date(`${date.value}T${time.value}:00`).toISOString()
  const jobId = props.editInterview?.job ?? candidate!.job

  loading.value = true
  error.value = ''
  try {
    const payload = {
      candidate: Number(candidateId.value),
      job: jobId,
      type: type.value,
      scheduled_at: scheduledAt,
      duration_min: durationMin.value,
      location: type.value === 'onsite' ? location.value : '',
      video_link: type.value === 'video' ? videoLink.value : '',
      status: status.value,
      interviewer_ids: interviewerIds.value,
    }
    if (props.editInterview) {
      await updateInterview(props.editInterview.id, payload)
    } else {
      await createInterview(payload)
    }
    emit('saved')
    emit('close')
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response?.data) {
      const data = err.response.data as Record<string, unknown>
      const first = Object.values(data).flat()[0]
      error.value = first ? String(first) : 'Could not save interview.'
    } else {
      error.value = 'Could not save interview.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div
    v-if="open"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4"
    @click.self="emit('close')"
  >
    <div class="bg-white rounded-xl shadow-lg w-full max-w-lg p-6 max-h-[90vh] overflow-y-auto">
      <h2 class="text-lg font-semibold text-sqli-midnight mb-4">
        {{ isEdit ? 'Edit interview' : 'Schedule interview' }}
      </h2>

      <div class="space-y-3 text-sm">
        <label class="block">
          <span class="text-gray-600">Candidate</span>
          <select
            v-model="candidateId"
            :disabled="Boolean(prefillCandidateId) || isEdit"
            required
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white disabled:opacity-60"
          >
            <option disabled value="">Select candidate</option>
            <option v-for="c in candidates" :key="c.id" :value="c.id">
              {{ c.first_name }} {{ c.last_name }} — {{ c.job_title }}
            </option>
          </select>
        </label>

        <p v-if="selectedCandidate" class="text-xs text-gray-500">
          Job: {{ selectedCandidate.job_title }}
        </p>

        <fieldset>
          <legend class="text-gray-600 mb-1">Type</legend>
          <div class="flex gap-4">
            <label v-for="opt in (['phone', 'video', 'onsite'] as const)" :key="opt" class="flex items-center gap-1.5">
              <input v-model="type" type="radio" :value="opt" />
              <span class="capitalize">{{ opt }}</span>
            </label>
          </div>
        </fieldset>

        <div class="grid grid-cols-2 gap-3">
          <label class="block">
            <span class="text-gray-600">Date</span>
            <input
              v-model="date"
              type="date"
              required
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2"
            />
          </label>
          <label class="block">
            <span class="text-gray-600">Time</span>
            <input
              v-model="time"
              type="time"
              required
              class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2"
            />
          </label>
        </div>

        <label class="block">
          <span class="text-gray-600">Duration</span>
          <select
            v-model="durationMin"
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white"
          >
            <option :value="30">30 min</option>
            <option :value="45">45 min</option>
            <option :value="60">60 min</option>
            <option :value="90">90 min</option>
          </select>
        </label>

        <label v-if="type === 'onsite'" class="block">
          <span class="text-gray-600">Location</span>
          <input
            v-model="location"
            type="text"
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2"
          />
        </label>

        <label v-if="type === 'video'" class="block">
          <span class="text-gray-600">Video link</span>
          <input
            v-model="videoLink"
            type="url"
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2"
          />
        </label>

        <label v-if="isEdit" class="block">
          <span class="text-gray-600">Status</span>
          <select
            v-model="status"
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white"
          >
            <option value="scheduled">Scheduled</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
            <option value="no_show">No show</option>
          </select>
        </label>

        <div>
          <p class="text-gray-600 mb-1">Interviewers</p>
          <div class="max-h-36 overflow-y-auto border border-gray-200 rounded-lg p-2 space-y-1">
            <label
              v-for="user in users"
              :key="user.id"
              class="flex items-center gap-2 px-1 py-1 hover:bg-sqli-cream rounded"
            >
              <input
                type="checkbox"
                :checked="interviewerIds.includes(user.id)"
                @change="toggleInterviewer(user.id)"
              />
              <span>
                {{ user.first_name }} {{ user.last_name }}
                <span class="text-xs text-gray-400">({{ user.role }})</span>
              </span>
            </label>
          </div>
        </div>
      </div>

      <p v-if="error" class="text-red-500 text-sm mt-3">{{ error }}</p>

      <div class="flex justify-end gap-2 mt-5">
        <button
          type="button"
          class="px-4 py-2 rounded-lg border border-gray-200 text-sm"
          @click="emit('close')"
        >
          Cancel
        </button>
        <button
          type="button"
          class="px-4 py-2 rounded-lg bg-sqli-cobalt text-white text-sm disabled:opacity-50"
          :disabled="loading"
          @click="submit"
        >
          {{ loading ? 'Saving…' : isEdit ? 'Save changes' : 'Schedule' }}
        </button>
      </div>
    </div>
  </div>
</template>
