<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'
import { fetchCandidate } from '@/api/candidates'
import AppLayout from '@/components/AppLayout.vue'
import CandidateStageBadge from '@/components/CandidateStageBadge.vue'
import type { Candidate } from '@/types/candidates'

const route = useRoute()
const candidate = ref<Candidate | null>(null)
const error = ref('')
const loading = ref(true)

onMounted(async () => {
  try {
    candidate.value = await fetchCandidate(Number(route.params.id))
  } catch {
    error.value = 'Candidate not found.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppLayout>
    <router-link to="/candidates" class="text-sm text-sqli-cobalt hover:underline mb-4 inline-block">
      ← Back to Candidates
    </router-link>

    <div v-if="loading" class="text-gray-500">Loading…</div>
    <p v-else-if="error" class="text-red-500">{{ error }}</p>

    <div v-else-if="candidate">
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
        </div>
        <CandidateStageBadge
          :name="candidate.current_stage_name"
          :color="candidate.current_stage_color"
        />
      </div>

      <div class="bg-white rounded-xl border border-sqli-gray-100 p-6 text-sm text-gray-600">
        <p class="text-sqli-midnight font-medium mb-2">Overview</p>
        <p v-if="candidate.linkedin" class="mb-1">
          LinkedIn:
          <a :href="candidate.linkedin" class="text-sqli-cobalt hover:underline" target="_blank">
            {{ candidate.linkedin }}
          </a>
        </p>
        <p v-if="candidate.resume_file" class="mb-1">
          Resume:
          <a :href="candidate.resume_file" class="text-sqli-cobalt hover:underline" target="_blank">
            Download
          </a>
        </p>
        <p class="text-gray-400 mt-4 text-xs">
          Full tabs (Timeline, Interviews, Scorecards, AI Brief) come in INT-026.
        </p>
      </div>
    </div>
  </AppLayout>
</template>
