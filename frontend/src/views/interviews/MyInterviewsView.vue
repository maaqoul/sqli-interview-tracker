<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { fetchInterviews } from '@/api/interviews'
import { fetchScorecards } from '@/api/scorecards'
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import type { Interview } from '@/types/interviews'
import { INTERVIEW_TYPE_LABELS } from '@/types/interviews'

const router = useRouter()
const auth = useAuthStore()

const interviews = ref<Interview[]>([])
const scoredIds = ref<Set<number>>(new Set())
const loading = ref(true)
const error = ref('')
const statusFilter = ref<'all' | 'scheduled' | 'completed'>('all')

const filtered = computed(() => {
  if (statusFilter.value === 'all') return interviews.value
  return interviews.value.filter((iv) => iv.status === statusFilter.value)
})

function formatWhen(iso: string) {
  return new Date(iso).toLocaleString('en-GB', {
    weekday: 'short',
    day: 'numeric',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

function canSubmit(iv: Interview) {
  return iv.status === 'scheduled' && !scoredIds.value.has(iv.id)
}

function goScorecard(id: number) {
  router.push(`/interviews/${id}/scorecard`)
}

async function load() {
  loading.value = true
  error.value = ''
  try {
    const [ivData, scData] = await Promise.all([
      fetchInterviews(),
      fetchScorecards(),
    ])
    interviews.value = ivData.results.sort((a, b) =>
      a.scheduled_at.localeCompare(b.scheduled_at),
    )
    scoredIds.value = new Set(
      scData.results
        .filter((s) => s.interviewer === auth.user?.id)
        .map((s) => s.interview),
    )
  } catch {
    error.value = 'Could not load your interviews.'
  } finally {
    loading.value = false
  }
}

onMounted(load)
</script>

<template>
  <AppLayout>
    <div class="flex items-center justify-between mb-6 gap-4 flex-wrap">
      <div>
        <h1 class="text-2xl font-semibold text-sqli-midnight">My Interviews</h1>
        <p class="text-gray-500 text-sm mt-1">Interviews assigned to you</p>
      </div>
      <div class="flex gap-2 text-sm">
        <button
          v-for="opt in [
            { value: 'all', label: 'All' },
            { value: 'scheduled', label: 'Scheduled' },
            { value: 'completed', label: 'Completed' },
          ]"
          :key="opt.value"
          type="button"
          class="px-3 py-1.5 rounded-lg border transition-colors"
          :class="
            statusFilter === opt.value
              ? 'border-sqli-cobalt bg-sqli-cobalt text-white'
              : 'border-gray-200 text-gray-600 hover:border-sqli-sky'
          "
          @click="statusFilter = opt.value as typeof statusFilter"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div v-if="loading" class="text-gray-500 text-sm">Loading…</div>
    <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>
    <div
      v-else-if="!filtered.length"
      class="bg-white rounded-xl border border-sqli-gray-100 p-8 text-center"
    >
      <p class="text-sqli-midnight font-medium">No interviews</p>
      <p class="text-sm text-gray-500 mt-1">Nothing assigned for this filter.</p>
    </div>
    <div v-else class="space-y-3">
      <div
        v-for="iv in filtered"
        :key="iv.id"
        class="bg-white rounded-xl border border-sqli-gray-100 p-4 flex flex-wrap items-center justify-between gap-3"
      >
        <div>
          <p class="font-medium text-sqli-midnight">{{ iv.candidate_name }}</p>
          <p class="text-sm text-gray-500 mt-0.5">
            {{ iv.job_title }} · {{ INTERVIEW_TYPE_LABELS[iv.type] }} ·
            {{ formatWhen(iv.scheduled_at) }}
          </p>
          <p class="text-xs text-gray-400 mt-1 capitalize">
            {{ iv.status.replace('_', ' ') }}
            <span v-if="scoredIds.has(iv.id)"> · Scorecard submitted</span>
          </p>
        </div>
        <button
          v-if="canSubmit(iv)"
          type="button"
          class="bg-sqli-cobalt hover:bg-[#003399] text-white text-sm font-medium px-4 py-2 rounded-lg"
          @click="goScorecard(iv.id)"
        >
          Submit scorecard
        </button>
        <span
          v-else-if="scoredIds.has(iv.id)"
          class="text-xs text-green-700 bg-green-50 px-2.5 py-1 rounded-lg"
        >
          Done
        </span>
      </div>
    </div>
  </AppLayout>
</template>
