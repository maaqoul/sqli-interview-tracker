<script setup lang="ts">
import type { JobStatus } from '@/types/jobs'

defineProps<{
  status: JobStatus
}>()

const labels: Record<JobStatus, string> = {
  open: 'Open',
  closed: 'Closed',
  on_hold: 'On hold',
}

const dotClass: Record<JobStatus, string> = {
  open: 'bg-green-500',
  closed: 'bg-gray-400',
  on_hold: 'bg-amber-500',
}
</script>

<template>
  <span class="inline-flex items-center gap-1.5 text-sm text-gray-700">
    <span class="w-2 h-2 rounded-full" :class="dotClass[status]" />
    {{ labels[status] }}
  </span>
</template>
