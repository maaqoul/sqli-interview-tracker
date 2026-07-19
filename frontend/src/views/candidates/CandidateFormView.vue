<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { createCandidate } from '@/api/candidates'
import { fetchJobs } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import type { CandidateSource } from '@/types/candidates'
import type { Job } from '@/types/jobs'

const router = useRouter()

const jobs = ref<Job[]>([])
const firstName = ref('')
const lastName = ref('')
const email = ref('')
const phone = ref('')
const linkedin = ref('')
const source = ref<CandidateSource>('linkedin')
const jobId = ref<number | ''>('')
const error = ref('')
const loading = ref(false)

const canSubmit = computed(
  () =>
    firstName.value.trim() &&
    lastName.value.trim() &&
    email.value.trim() &&
    jobId.value !== '',
)

onMounted(async () => {
  try {
    const data = await fetchJobs('open')
    jobs.value = data.results
  } catch {
    error.value = 'Could not load jobs.'
  }
})

async function handleSubmit() {
  if (!canSubmit.value || jobId.value === '') return
  loading.value = true
  error.value = ''
  try {
    const candidate = await createCandidate({
      first_name: firstName.value.trim(),
      last_name: lastName.value.trim(),
      email: email.value.trim(),
      phone: phone.value.trim(),
      linkedin: linkedin.value.trim(),
      source: source.value,
      job: Number(jobId.value),
    })
    router.push(`/candidates/${candidate.id}`)
  } catch (err: unknown) {
    if (axios.isAxiosError(err) && err.response?.data) {
      const data = err.response.data as Record<string, unknown>
      const first = Object.values(data).flat()[0]
      error.value = first ? String(first) : 'Could not create candidate.'
    } else {
      error.value = 'Could not create candidate.'
    }
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppLayout>
    <router-link to="/candidates" class="text-sm text-sqli-cobalt hover:underline mb-4 inline-block">
      ← Back to Candidates
    </router-link>

    <h1 class="text-2xl font-semibold text-sqli-midnight mb-6">Add Candidate</h1>

    <form
      class="bg-white rounded-xl border border-sqli-gray-100 p-8 max-w-xl space-y-4"
      @submit.prevent="handleSubmit"
    >
      <div class="grid grid-cols-2 gap-4">
        <label class="block">
          <span class="text-sm text-gray-600">First name</span>
          <input
            v-model="firstName"
            required
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky"
          />
        </label>
        <label class="block">
          <span class="text-sm text-gray-600">Last name</span>
          <input
            v-model="lastName"
            required
            class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky"
          />
        </label>
      </div>

      <label class="block">
        <span class="text-sm text-gray-600">Email</span>
        <input
          v-model="email"
          type="email"
          required
          class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky"
        />
      </label>

      <label class="block">
        <span class="text-sm text-gray-600">Phone</span>
        <input
          v-model="phone"
          type="tel"
          class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky"
        />
      </label>

      <label class="block">
        <span class="text-sm text-gray-600">LinkedIn URL</span>
        <input
          v-model="linkedin"
          type="url"
          class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky"
        />
      </label>

      <label class="block">
        <span class="text-sm text-gray-600">Job opening</span>
        <select
          v-model="jobId"
          required
          class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-sqli-sky"
        >
          <option disabled value="">Select a job</option>
          <option v-for="job in jobs" :key="job.id" :value="job.id">{{ job.title }}</option>
        </select>
      </label>

      <label class="block">
        <span class="text-sm text-gray-600">Source</span>
        <select
          v-model="source"
          class="mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-sqli-sky"
        >
          <option value="linkedin">LinkedIn</option>
          <option value="referral">Referral</option>
          <option value="job_board">Job board</option>
          <option value="other">Other</option>
        </select>
      </label>

      <p v-if="error" class="text-red-500 text-sm">{{ error }}</p>

      <div class="flex gap-3 pt-2">
        <button
          type="button"
          class="px-4 py-2.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-sqli-cream"
          @click="router.push('/candidates')"
        >
          Cancel
        </button>
        <button
          type="submit"
          :disabled="loading || !canSubmit"
          class="bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-4 py-2.5 rounded-lg disabled:opacity-50"
        >
          {{ loading ? 'Saving…' : 'Save Candidate' }}
        </button>
      </div>
    </form>
  </AppLayout>
</template>
