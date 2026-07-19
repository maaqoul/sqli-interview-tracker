<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { fetchInterview } from '@/api/interviews'
import { fetchScorecards, submitScorecard } from '@/api/scorecards'
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'
import type { Interview } from '@/types/interviews'
import {
  RECOMMENDATION_OPTIONS,
  SKILL_LABELS,
  type Recommendation,
  type SkillRatings,
} from '@/types/scorecards'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const interviewId = computed(() => Number(route.params.id))
const interview = ref<Interview | null>(null)
const alreadySubmitted = ref(false)

const overall = ref(0)
const skills = ref<SkillRatings>({
  technical: 0,
  communication: 0,
  problem_solving: 0,
  culture_fit: 0,
  leadership: 0,
})
const recommendation = ref<Recommendation | ''>('')
const strengths = ref('')
const weaknesses = ref('')
const privateNotes = ref('')

const error = ref('')
const loading = ref(false)
const pageLoading = ref(true)

const skillKeys = Object.keys(SKILL_LABELS) as (keyof SkillRatings)[]

const inputClass =
  'mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky'

function setOverall(n: number) {
  overall.value = n
}

function setSkill(key: keyof SkillRatings, n: number) {
  skills.value = { ...skills.value, [key]: n }
}

function validate(): boolean {
  error.value = ''
  if (overall.value < 1 || overall.value > 5) {
    error.value = 'Overall rating is required.'
    return false
  }
  for (const key of skillKeys) {
    if (skills.value[key] < 1 || skills.value[key] > 5) {
      error.value = `Please rate ${SKILL_LABELS[key]}.`
      return false
    }
  }
  if (!recommendation.value) {
    error.value = 'Recommendation is required.'
    return false
  }
  return true
}

async function handleSubmit() {
  if (!validate() || !recommendation.value) return

  loading.value = true
  error.value = ''
  try {
    await submitScorecard({
      interview: interviewId.value,
      overall_rating: overall.value,
      skill_ratings: { ...skills.value },
      strengths: strengths.value.trim(),
      weaknesses: weaknesses.value.trim(),
      recommendation: recommendation.value,
      private_notes: privateNotes.value.trim(),
    })
    await router.push('/my-interviews')
  } catch (err) {
    if (axios.isAxiosError(err)) {
      const data = err.response?.data as Record<string, unknown> | undefined
      error.value =
        (typeof data?.detail === 'string' && data.detail) ||
        (typeof data?.interview === 'object' &&
          Array.isArray(data.interview) &&
          String(data.interview[0])) ||
        'Could not submit scorecard.'
    } else {
      error.value = 'Could not submit scorecard.'
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  pageLoading.value = true
  try {
    interview.value = await fetchInterview(interviewId.value)
    const existing = await fetchScorecards({ interview_id: interviewId.value })
    alreadySubmitted.value = existing.results.some((s) => s.interviewer === auth.user?.id)
  } catch {
    error.value = 'Could not load interview.'
  } finally {
    pageLoading.value = false
  }
})
</script>

<template>
  <AppLayout>
    <router-link
      to="/my-interviews"
      class="text-sm text-sqli-cobalt hover:underline mb-4 inline-block"
    >
      ← My Interviews
    </router-link>

    <div v-if="pageLoading" class="text-gray-500 text-sm">Loading…</div>

    <div v-else-if="alreadySubmitted" class="bg-white rounded-xl border border-sqli-gray-100 p-8">
      <h1 class="text-xl font-semibold text-sqli-midnight">Scorecard already submitted</h1>
      <p class="text-sm text-gray-500 mt-2">
        You already submitted a scorecard for this interview.
      </p>
      <router-link
        to="/my-interviews"
        class="inline-block mt-4 text-sm text-sqli-cobalt hover:underline"
      >
        Back to My Interviews
      </router-link>
    </div>

    <form
      v-else-if="interview"
      class="max-w-2xl space-y-6"
      @submit.prevent="handleSubmit"
    >
      <div>
        <h1 class="text-2xl font-semibold text-sqli-midnight">Submit scorecard</h1>
        <p class="text-sm text-gray-500 mt-1">
          {{ interview.candidate_name }} · {{ interview.job_title }} ·
          {{ new Date(interview.scheduled_at).toLocaleString('en-GB') }}
        </p>
      </div>

      <div class="bg-white rounded-xl border border-sqli-gray-100 p-6 space-y-6">
        <div>
          <p class="text-sm font-medium text-sqli-midnight mb-2">Overall rating</p>
          <div class="flex gap-1">
            <button
              v-for="n in 5"
              :key="n"
              type="button"
              class="text-2xl leading-none transition-colors"
              :style="{ color: n <= overall ? '#F59E0B' : '#D1D5DB' }"
              :aria-label="`${n} stars`"
              @click="setOverall(n)"
            >
              ★
            </button>
          </div>
        </div>

        <div class="space-y-4">
          <p class="text-sm font-medium text-sqli-midnight">Skill ratings</p>
          <div v-for="key in skillKeys" :key="key" class="flex items-center justify-between gap-4">
            <span class="text-sm text-gray-600 w-40 shrink-0">{{ SKILL_LABELS[key] }}</span>
            <div class="flex gap-1">
              <button
                v-for="n in 5"
                :key="n"
                type="button"
                class="text-xl leading-none transition-colors"
                :style="{ color: n <= skills[key] ? '#F59E0B' : '#D1D5DB' }"
                :aria-label="`${SKILL_LABELS[key]} ${n}`"
                @click="setSkill(key, n)"
              >
                ★
              </button>
            </div>
          </div>
        </div>

        <div>
          <label class="text-sm font-medium text-sqli-midnight" for="recommendation">
            Recommendation
          </label>
          <select id="recommendation" v-model="recommendation" :class="inputClass" required>
            <option disabled value="">Select…</option>
            <option
              v-for="opt in RECOMMENDATION_OPTIONS"
              :key="opt.value"
              :value="opt.value"
            >
              {{ opt.label }}
            </option>
          </select>
        </div>

        <div>
          <label class="text-sm font-medium text-sqli-midnight" for="strengths">Strengths</label>
          <textarea id="strengths" v-model="strengths" rows="3" :class="inputClass" />
        </div>

        <div>
          <label class="text-sm font-medium text-sqli-midnight" for="weaknesses">
            Weaknesses
          </label>
          <textarea id="weaknesses" v-model="weaknesses" rows="3" :class="inputClass" />
        </div>

        <div>
          <label class="text-sm font-medium text-sqli-midnight" for="private-notes">
            Private notes
          </label>
          <p class="text-xs text-gray-400 mt-0.5">Visible to recruiters and admins only.</p>
          <textarea id="private-notes" v-model="privateNotes" rows="3" :class="inputClass" />
        </div>
      </div>

      <p v-if="error" class="text-sm text-red-600">{{ error }}</p>

      <div class="flex gap-3">
        <button
          type="submit"
          class="bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-5 py-2.5 rounded-lg disabled:opacity-50"
          :disabled="loading"
        >
          {{ loading ? 'Submitting…' : 'Submit scorecard' }}
        </button>
        <button
          type="button"
          class="px-4 py-2.5 rounded-lg border border-gray-200 text-sm"
          @click="router.push('/my-interviews')"
        >
          Cancel
        </button>
      </div>
    </form>

    <p v-else class="text-sm text-red-600">{{ error || 'Interview not found.' }}</p>
  </AppLayout>
</template>
