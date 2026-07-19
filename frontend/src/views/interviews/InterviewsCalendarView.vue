<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { fetchInterviews, updateInterview } from '@/api/interviews'
import AppLayout from '@/components/AppLayout.vue'
import AppToast from '@/components/AppToast.vue'
import ScheduleInterviewModal from '@/components/ScheduleInterviewModal.vue'
import { useAuthStore } from '@/stores/auth'
import type { Interview } from '@/types/interviews'
import { INTERVIEW_TYPE_COLORS, INTERVIEW_TYPE_LABELS } from '@/types/interviews'

const auth = useAuthStore()

const weekStart = ref(startOfWeek(new Date()))
const interviews = ref<Interview[]>([])
const loading = ref(true)
const error = ref('')
const toast = ref('')

const showSchedule = ref(false)
const selected = ref<Interview | null>(null)
const editing = ref<Interview | null>(null)

const canManage = computed(
  () => auth.user?.role === 'recruiter' || auth.user?.role === 'admin',
)

const weekDays = computed(() => {
  const days: Date[] = []
  for (let i = 0; i < 7; i++) {
    const d = new Date(weekStart.value)
    d.setDate(d.getDate() + i)
    days.push(d)
  }
  return days
})

const weekLabel = computed(() => {
  const start = weekDays.value[0]
  const end = weekDays.value[6]
  const opts: Intl.DateTimeFormatOptions = { month: 'short', day: 'numeric', year: 'numeric' }
  return `${start.toLocaleDateString('en-GB', opts)} – ${end.toLocaleDateString('en-GB', opts)}`
})

function startOfWeek(date: Date) {
  const d = new Date(date)
  d.setHours(0, 0, 0, 0)
  const day = d.getDay()
  const diff = day === 0 ? -6 : 1 - day
  d.setDate(d.getDate() + diff)
  return d
}

function toDateKey(d: Date) {
  return d.toISOString().slice(0, 10)
}

function interviewsForDay(day: Date) {
  const key = toDateKey(day)
  return interviews.value
    .filter((iv) => iv.scheduled_at.slice(0, 10) === key)
    .sort((a, b) => a.scheduled_at.localeCompare(b.scheduled_at))
}

function formatTime(iso: string) {
  return new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit' })
}

function shiftWeek(delta: number) {
  const d = new Date(weekStart.value)
  d.setDate(d.getDate() + delta * 7)
  weekStart.value = d
}

function showToast(msg: string) {
  toast.value = msg
  setTimeout(() => {
    toast.value = ''
  }, 3000)
}

async function loadInterviews() {
  loading.value = true
  error.value = ''
  try {
    const from = toDateKey(weekDays.value[0])
    const to = toDateKey(weekDays.value[6])
    const data = await fetchInterviews({ date_from: from, date_to: to })
    interviews.value = data.results
  } catch {
    error.value = 'Could not load interviews.'
  } finally {
    loading.value = false
  }
}

async function cancelInterview(iv: Interview) {
  try {
    await updateInterview(iv.id, { status: 'cancelled' })
    selected.value = null
    showToast('Interview cancelled.')
    await loadInterviews()
  } catch {
    showToast('Could not cancel interview.')
  }
}

function openSchedule() {
  editing.value = null
  showSchedule.value = true
}

function openEditFromDetail() {
  editing.value = selected.value
  selected.value = null
  showSchedule.value = true
}

function closeSchedule() {
  showSchedule.value = false
  editing.value = null
}

async function onScheduleSaved() {
  showToast(editing.value ? 'Interview updated.' : 'Interview scheduled.')
  await loadInterviews()
}

watch(weekStart, loadInterviews)
onMounted(loadInterviews)
</script>

<template>
  <AppLayout>
    <div class="flex items-center justify-between mb-6 gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-semibold text-sqli-midnight">Interviews</h1>
        <p class="text-gray-500 text-sm mt-1">Week calendar of scheduled interviews</p>
      </div>
      <button
        v-if="canManage"
        type="button"
        class="bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-4 py-2.5 rounded-lg"
        @click="openSchedule"
      >
        + Schedule Interview
      </button>
    </div>

    <div class="flex items-center justify-between mb-4 gap-3 flex-wrap">
      <div class="flex items-center gap-2">
        <button
          type="button"
          class="px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-sm"
          @click="shiftWeek(-1)"
        >
          ◀
        </button>
        <p class="text-sm font-medium text-sqli-midnight min-w-[220px] text-center">
          {{ weekLabel }}
        </p>
        <button
          type="button"
          class="px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-sm"
          @click="shiftWeek(1)"
        >
          ▶
        </button>
        <button
          type="button"
          class="px-3 py-1.5 rounded-lg border border-gray-200 bg-white text-sm"
          @click="weekStart = startOfWeek(new Date())"
        >
          Today
        </button>
      </div>
      <div class="flex gap-3 text-xs text-gray-600">
        <span v-for="(color, key) in INTERVIEW_TYPE_COLORS" :key="key" class="inline-flex items-center gap-1">
          <span class="w-2.5 h-2.5 rounded-sm" :style="{ backgroundColor: color }" />
          {{ INTERVIEW_TYPE_LABELS[key] }}
        </span>
      </div>
    </div>

    <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>
    <p v-if="loading" class="text-gray-500 text-sm mb-4">Loading…</p>

    <div class="grid grid-cols-7 gap-2 min-h-[420px]">
      <div
        v-for="day in weekDays"
        :key="toDateKey(day)"
        class="bg-white rounded-xl border border-sqli-gray-100 flex flex-col min-h-[400px]"
      >
        <div class="px-2 py-2 border-b border-sqli-gray-100 text-center">
          <p class="text-xs text-gray-500 uppercase">
            {{ day.toLocaleDateString('en-GB', { weekday: 'short' }) }}
          </p>
          <p class="text-sm font-semibold text-sqli-midnight">{{ day.getDate() }}</p>
        </div>
        <div class="p-2 space-y-2 flex-1">
          <button
            v-for="iv in interviewsForDay(day)"
            :key="iv.id"
            type="button"
            class="w-full text-left rounded-lg p-2 text-white text-xs shadow-sm hover:opacity-90"
            :style="{ backgroundColor: INTERVIEW_TYPE_COLORS[iv.type] }"
            :class="{ 'opacity-50': iv.status === 'cancelled' }"
            @click="selected = iv"
          >
            <p class="font-semibold">{{ formatTime(iv.scheduled_at) }}</p>
            <p class="truncate">{{ iv.candidate_name }}</p>
            <p class="opacity-90">{{ INTERVIEW_TYPE_LABELS[iv.type] }}</p>
          </button>
        </div>
      </div>
    </div>

    <!-- Detail modal -->
    <div
      v-if="selected"
      class="fixed inset-0 z-40 flex items-center justify-center bg-black/40 p-4"
      @click.self="selected = null"
    >
      <div class="bg-white rounded-xl shadow-lg w-full max-w-md p-6">
        <h2 class="text-lg font-semibold text-sqli-midnight mb-1">
          {{ selected.candidate_name }}
        </h2>
        <p class="text-sm text-gray-500 mb-4">{{ selected.job_title }}</p>
        <dl class="text-sm space-y-2 text-gray-600">
          <div class="flex justify-between">
            <dt>Type</dt>
            <dd class="font-medium text-sqli-midnight">
              {{ INTERVIEW_TYPE_LABELS[selected.type] }}
            </dd>
          </div>
          <div class="flex justify-between">
            <dt>When</dt>
            <dd class="font-medium text-sqli-midnight">
              {{ new Date(selected.scheduled_at).toLocaleString('en-GB') }}
            </dd>
          </div>
          <div class="flex justify-between">
            <dt>Duration</dt>
            <dd>{{ selected.duration_min }} min</dd>
          </div>
          <div class="flex justify-between">
            <dt>Status</dt>
            <dd class="capitalize">{{ selected.status.replace('_', ' ') }}</dd>
          </div>
          <div>
            <dt class="mb-1">Interviewers</dt>
            <dd>{{ selected.interviewer_names.join(', ') || '—' }}</dd>
          </div>
          <div v-if="selected.video_link">
            <dt>Video</dt>
            <dd>
              <a :href="selected.video_link" class="text-sqli-cobalt hover:underline" target="_blank">
                Join link
              </a>
            </dd>
          </div>
          <div v-if="selected.location">
            <dt>Location</dt>
            <dd>{{ selected.location }}</dd>
          </div>
        </dl>

        <div class="flex flex-wrap justify-end gap-2 mt-6">
          <button
            type="button"
            class="px-3 py-2 rounded-lg border border-gray-200 text-sm"
            @click="selected = null"
          >
            Close
          </button>
          <button
            v-if="canManage"
            type="button"
            class="px-3 py-2 rounded-lg border border-gray-200 text-sm"
            @click="openEditFromDetail"
          >
            Edit
          </button>
          <button
            v-if="canManage && selected.status === 'scheduled'"
            type="button"
            class="px-3 py-2 rounded-lg bg-red-600 text-white text-sm"
            @click="cancelInterview(selected)"
          >
            Cancel interview
          </button>
        </div>
      </div>
    </div>

    <ScheduleInterviewModal
      :open="showSchedule"
      :edit-interview="editing"
      @close="closeSchedule"
      @saved="onScheduleSaved"
    />

    <AppToast :message="toast" />
  </AppLayout>
</template>
