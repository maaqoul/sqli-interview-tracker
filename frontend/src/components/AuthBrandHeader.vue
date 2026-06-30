<script setup lang="ts">
function onLogoError(event: Event) {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
  const fallback = img.nextElementSibling as HTMLElement | null
  if (fallback) fallback.classList.remove('hidden')
}
</script>

<template>
  <div class="text-center mb-8">
    <img
      src="/assets/sqli-logo.svg"
      alt="SQLI"
      class="h-10 mx-auto"
      @error="onLogoError"
    />
    <div class="hidden text-3xl font-bold text-sqli-midnight tracking-tight">SQLI</div>
    <p class="text-sqli-cobalt mt-3 text-sm font-medium">We Elevate. Digitally.</p>
    <p class="text-gray-500 mt-1 text-sm">Interview Tracker</p>
  </div>
</template>
