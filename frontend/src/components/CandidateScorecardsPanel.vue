<script setup lang="ts">
import { computed } from 'vue'
import type { Scorecard } from '@/types/scorecards'
import { SKILL_LABELS, type SkillRatings } from '@/types/scorecards'
import {
  aggregateScorecards,
  recommendationLabel,
  starsDisplay,
} from '@/utils/scorecardAggregate'

const props = defineProps<{
  scorecards: Scorecard[]
  canSeePrivateNotes?: boolean
}>()

const aggregate = computed(() => aggregateScorecards(props.scorecards))
const skillKeys = Object.keys(SKILL_LABELS) as (keyof SkillRatings)[]

function formatWhen(iso: string) {
  return new Date(iso).toLocaleString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}
</script>

<template>
  <div class="space-y-6">
    <div
      v-if="!scorecards.length"
      class="bg-white rounded-xl border border-sqli-gray-100 p-8 text-center"
    >
      <p class="text-sqli-midnight font-medium">No scorecards yet</p>
      <p class="text-sm text-gray-500 mt-1">
        Interviewers submit scorecards from My Interviews after each interview.
      </p>
    </div>

    <template v-else>
      <!-- Summary -->
      <div class="bg-white rounded-xl border border-sqli-gray-100 p-6">
        <h2 class="text-lg font-semibold text-sqli-midnight mb-1">Scorecard summary</h2>
        <p class="text-sm text-gray-500 mb-5">
          Based on {{ aggregate.count }} scorecard{{ aggregate.count === 1 ? '' : 's' }}
        </p>

        <div class="grid sm:grid-cols-3 gap-4 mb-6">
          <div class="rounded-lg bg-sqli-cream/60 p-4">
            <p class="text-xs uppercase tracking-wide text-gray-400 mb-1">Avg overall</p>
            <p class="text-2xl font-semibold text-sqli-midnight">
              {{ aggregate.averageOverall }}/5
            </p>
            <p class="text-sm mt-1" style="color: #f59e0b">
              {{ starsDisplay(aggregate.averageOverall ?? 0) }}
            </p>
          </div>
          <div class="rounded-lg bg-sqli-cream/60 p-4 sm:col-span-2">
            <p class="text-xs uppercase tracking-wide text-gray-400 mb-1">Consensus</p>
            <p class="text-xl font-semibold text-sqli-midnight">{{ aggregate.consensusLabel }}</p>
            <p class="text-sm text-gray-500 mt-1">
              <span v-for="(row, i) in aggregate.breakdown" :key="row.value">
                {{ row.count }}× {{ row.label
                }}<span v-if="i < aggregate.breakdown.length - 1"> · </span>
              </span>
            </p>
          </div>
        </div>

        <div>
          <p class="text-sm font-medium text-sqli-midnight mb-3">Average skill ratings</p>
          <div class="space-y-2">
            <div
              v-for="key in skillKeys"
              :key="key"
              class="flex items-center justify-between gap-4 text-sm"
            >
              <span class="text-gray-600 w-40 shrink-0">{{ SKILL_LABELS[key] }}</span>
              <div class="flex-1 h-2 rounded-full bg-gray-100 overflow-hidden">
                <div
                  class="h-full rounded-full bg-sqli-cobalt"
                  :style="{
                    width: `${((aggregate.averageSkills[key] ?? 0) / 5) * 100}%`,
                  }"
                />
              </div>
              <span class="tabular-nums text-sqli-midnight w-10 text-right">
                {{ aggregate.averageSkills[key] ?? '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Individual scorecards -->
      <div class="space-y-3">
        <h3 class="text-sm font-medium text-sqli-midnight">Individual scorecards</h3>
        <div
          v-for="sc in scorecards"
          :key="sc.id"
          class="bg-white rounded-xl border border-sqli-gray-100 p-5"
        >
          <div class="flex flex-wrap items-start justify-between gap-2 mb-3">
            <div>
              <p class="font-medium text-sqli-midnight">{{ sc.interviewer_name }}</p>
              <p class="text-xs text-gray-400 mt-0.5 capitalize">
                {{ sc.interview_type }} · {{ formatWhen(sc.submitted_at) }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-sm font-medium text-sqli-midnight">
                {{ sc.overall_rating }}/5
                <span style="color: #f59e0b">{{ starsDisplay(sc.overall_rating) }}</span>
              </p>
              <p class="text-xs text-sqli-cobalt mt-0.5">
                {{ recommendationLabel(sc.recommendation) }}
              </p>
            </div>
          </div>

          <div class="grid sm:grid-cols-5 gap-2 text-xs text-gray-500 mb-3">
            <div v-for="key in skillKeys" :key="key">
              <span class="block text-gray-400">{{ SKILL_LABELS[key] }}</span>
              {{ sc.skill_ratings[key] }}/5
            </div>
          </div>

          <div v-if="sc.strengths" class="text-sm mb-2">
            <span class="text-gray-400 text-xs uppercase">Strengths</span>
            <p class="text-gray-700 mt-0.5 whitespace-pre-wrap">{{ sc.strengths }}</p>
          </div>
          <div v-if="sc.weaknesses" class="text-sm mb-2">
            <span class="text-gray-400 text-xs uppercase">Weaknesses</span>
            <p class="text-gray-700 mt-0.5 whitespace-pre-wrap">{{ sc.weaknesses }}</p>
          </div>
          <div
            v-if="canSeePrivateNotes && sc.private_notes"
            class="text-sm mt-2 pt-2 border-t border-sqli-gray-100"
          >
            <span class="text-gray-400 text-xs uppercase">Private notes</span>
            <p class="text-gray-700 mt-0.5 whitespace-pre-wrap">{{ sc.private_notes }}</p>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>
