<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import draggable from 'vuedraggable'
import { moveCandidateStage } from '@/api/candidates'
import type { Candidate } from '@/types/candidates'
import type { PipelineStage } from '@/types/jobs'

const props = defineProps<{
  candidates: Candidate[]
  stages: PipelineStage[]
  canMove: boolean
}>()

const emit = defineEmits<{
  moved: []
  error: [message: string]
}>()

const columns = ref<Record<number, Candidate[]>>({})
const moving = ref(false)

function daysInStage(candidate: Candidate) {
  const start = new Date(candidate.updated_at).getTime()
  const days = Math.max(0, Math.floor((Date.now() - start) / (1000 * 60 * 60 * 24)))
  return days === 0 ? 'today' : `${days}d in stage`
}

function rebuildColumns() {
  const next: Record<number, Candidate[]> = {}
  for (const stage of props.stages) {
    next[stage.id] = []
  }
  for (const candidate of props.candidates) {
    if (!next[candidate.current_stage]) {
      next[candidate.current_stage] = []
    }
    next[candidate.current_stage].push(candidate)
  }
  columns.value = next
}

watch(
  () => [props.candidates, props.stages] as const,
  () => rebuildColumns(),
  { immediate: true, deep: true },
)

const orderedStages = computed(() => [...props.stages].sort((a, b) => a.order - b.order))

async function onChange(stage: PipelineStage, event: { added?: { element: Candidate } }) {
  if (!event.added || !props.canMove || moving.value) return

  const candidate = event.added.element
  if (candidate.current_stage === stage.id) return

  moving.value = true
  try {
    await moveCandidateStage(candidate.id, {
      stage_id: stage.id,
      reason: `Moved to ${stage.name} via kanban`,
    })
    emit('moved')
  } catch {
    rebuildColumns()
    emit('error', 'Could not move candidate. Try again.')
  } finally {
    moving.value = false
  }
}
</script>

<template>
  <div class="flex gap-4 overflow-x-auto pb-4">
    <div
      v-for="stage in orderedStages"
      :key="stage.id"
      class="w-64 shrink-0 bg-white rounded-xl border border-sqli-gray-100 flex flex-col min-h-[320px]"
      :style="{ borderTopWidth: '3px', borderTopColor: stage.color }"
    >
      <div class="px-3 py-3 flex items-center justify-between border-b border-sqli-gray-100">
        <span class="text-sm font-medium text-sqli-midnight">{{ stage.name }}</span>
        <span class="text-xs bg-sqli-gray-100 text-gray-600 rounded-full px-2 py-0.5">
          {{ columns[stage.id]?.length ?? 0 }}
        </span>
      </div>

      <draggable
        v-model="columns[stage.id]"
        group="candidates"
        item-key="id"
        class="flex-1 p-2 space-y-2 min-h-[200px]"
        :disabled="!canMove || moving"
        @change="(e: { added?: { element: Candidate } }) => onChange(stage, e)"
      >
        <template #item="{ element }">
          <div
            class="bg-white border border-sqli-gray-100 rounded-lg p-3 shadow-sm hover:shadow cursor-grab active:cursor-grabbing"
          >
            <p class="font-medium text-sm text-sqli-midnight">
              {{ element.first_name }} {{ element.last_name }}
            </p>
            <p class="text-xs text-gray-500 mt-0.5 truncate">{{ element.job_title }}</p>
            <p class="text-[11px] text-gray-400 mt-1">{{ daysInStage(element) }}</p>
          </div>
        </template>
      </draggable>

      <p
        v-if="(columns[stage.id]?.length ?? 0) === 0"
        class="mx-2 mb-3 text-xs text-center text-gray-400 border border-dashed border-gray-200 rounded-lg py-6"
      >
        Drop candidates here
      </p>
    </div>
  </div>
</template>
