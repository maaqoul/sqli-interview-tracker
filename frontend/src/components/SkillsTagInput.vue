<script setup lang="ts">
import { ref } from 'vue'

const skills = defineModel<string[]>({ default: () => [] })
const input = ref('')

function addSkill() {
  const value = input.value.trim()
  if (!value) return
  if (!skills.value.includes(value)) {
    skills.value = [...skills.value, value]
  }
  input.value = ''
}

function removeSkill(skill: string) {
  skills.value = skills.value.filter((s) => s !== skill)
}

function onKeydown(event: KeyboardEvent) {
  if (event.key === 'Enter') {
    event.preventDefault()
    addSkill()
  }
}
</script>

<template>
  <div>
    <div class="flex flex-wrap gap-2 mb-2">
      <span
        v-for="skill in skills"
        :key="skill"
        class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full bg-sqli-gray-100 text-sm text-sqli-midnight"
      >
        {{ skill }}
        <button
          type="button"
          class="text-gray-500 hover:text-red-500 leading-none"
          @click="removeSkill(skill)"
        >
          ×
        </button>
      </span>
    </div>
    <input
      v-model="input"
      type="text"
      placeholder="Type a skill and press Enter"
      class="w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky"
      @keydown="onKeydown"
    />
  </div>
</template>
