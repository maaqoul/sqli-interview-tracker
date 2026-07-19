<script setup lang="ts">
import { computed } from 'vue'
import CandidateStageBadge from '@/components/CandidateStageBadge.vue'
import type { Candidate } from '@/types/candidates'

const props = defineProps<{
  candidates: Candidate[]
  sortKey: string
  sortDir: 'asc' | 'desc'
}>()

const emit = defineEmits<{
  sort: [key: string]
  select: [id: number]
}>()

const sourceLabels: Record<string, string> = {
  linkedin: 'LinkedIn',
  referral: 'Referral',
  job_board: 'Job board',
  other: 'Other',
  '': '—',
}

const sorted = computed(() => {
  const list = [...props.candidates]
  const dir = props.sortDir === 'asc' ? 1 : -1
  list.sort((a, b) => {
    const key = props.sortKey
    let av: string | number = ''
    let bv: string | number = ''
    if (key === 'name') {
      av = `${a.first_name} ${a.last_name}`.toLowerCase()
      bv = `${b.first_name} ${b.last_name}`.toLowerCase()
    } else if (key === 'job') {
      av = a.job_title.toLowerCase()
      bv = b.job_title.toLowerCase()
    } else if (key === 'stage') {
      av = a.current_stage_name.toLowerCase()
      bv = b.current_stage_name.toLowerCase()
    } else if (key === 'date') {
      av = a.created_at
      bv = b.created_at
    } else if (key === 'source') {
      av = a.source || ''
      bv = b.source || ''
    }
    if (av < bv) return -1 * dir
    if (av > bv) return 1 * dir
    return 0
  })
  return list
})

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-GB', {
    day: 'numeric',
    month: 'short',
    year: 'numeric',
  })
}

function sortLabel(key: string) {
  if (props.sortKey !== key) return ''
  return props.sortDir === 'asc' ? ' ▲' : ' ▼'
}
</script>

<template>
  <div class="bg-white rounded-xl border border-sqli-gray-100 overflow-hidden">
    <table class="w-full text-sm">
      <thead class="bg-sqli-gray-100/50 text-left text-gray-600">
        <tr>
          <th
            class="px-4 py-3 font-medium cursor-pointer select-none"
            @click="emit('sort', 'name')"
          >
            Name{{ sortLabel('name') }}
          </th>
          <th
            class="px-4 py-3 font-medium cursor-pointer select-none"
            @click="emit('sort', 'job')"
          >
            Job{{ sortLabel('job') }}
          </th>
          <th
            class="px-4 py-3 font-medium cursor-pointer select-none"
            @click="emit('sort', 'stage')"
          >
            Stage{{ sortLabel('stage') }}
          </th>
          <th
            class="px-4 py-3 font-medium cursor-pointer select-none"
            @click="emit('sort', 'date')"
          >
            Date{{ sortLabel('date') }}
          </th>
          <th
            class="px-4 py-3 font-medium cursor-pointer select-none"
            @click="emit('sort', 'source')"
          >
            Source{{ sortLabel('source') }}
          </th>
        </tr>
      </thead>
      <tbody>
        <tr
          v-for="c in sorted"
          :key="c.id"
          class="border-t border-sqli-gray-100 hover:bg-sqli-cream/50 cursor-pointer"
          @click="emit('select', c.id)"
        >
          <td class="px-4 py-3 font-medium text-sqli-midnight">
            {{ c.first_name }} {{ c.last_name }}
          </td>
          <td class="px-4 py-3 text-gray-600">{{ c.job_title }}</td>
          <td class="px-4 py-3">
            <CandidateStageBadge :name="c.current_stage_name" :color="c.current_stage_color" />
          </td>
          <td class="px-4 py-3 text-gray-600">{{ formatDate(c.created_at) }}</td>
          <td class="px-4 py-3 text-gray-600">{{ sourceLabels[c.source] ?? '—' }}</td>
        </tr>
      </tbody>
    </table>
  </div>
</template>
