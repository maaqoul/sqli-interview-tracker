<script setup lang="ts">
defineProps<{
  name: string
  color: string
}>()
</script>

<template>
  <span class="inline-flex items-center gap-1.5 text-sm text-sqli-midnight">
    <span
      class="inline-block w-2 h-2 rounded-full shrink-0"
      :style="{ backgroundColor: color || '#6B7280' }"
    />
    {{ name }}
  </span>
</template>
