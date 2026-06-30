<script setup lang="ts">
defineProps<{
  message: string
}>()
</script>

<template>
  <div
    v-if="message"
    class="fixed bottom-6 right-6 z-50 px-4 py-3 rounded-lg bg-sqli-midnight text-white text-sm shadow-lg"
    role="status"
  >
    {{ message }}
  </div>
</template>
