<script setup lang="ts">
import axios from 'axios'
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { createJob, fetchJob, updateJob } from '@/api/jobs'
import AppLayout from '@/components/AppLayout.vue'
import SkillsTagInput from '@/components/SkillsTagInput.vue'
import type { JobLevel, JobPayload, JobStatus } from '@/types/jobs'

const route = useRoute()
const router = useRouter()

const isEdit = computed(() => route.name === 'job-edit')
const jobId = computed(() => (isEdit.value ? Number(route.params.id) : null))

const title = ref('')
const department = ref('')
const location = ref('')
const level = ref<JobLevel>('mid')
const description = ref('')
const skills = ref<string[]>([])
const status = ref<JobStatus>('open')

const titleError = ref('')
const departmentError = ref('')
const locationError = ref('')
const descriptionError = ref('')
const error = ref('')
const loading = ref(false)
const pageLoading = ref(false)

const inputClass =
  'mt-1 w-full rounded-lg border border-gray-200 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky'
const inputErrorClass =
  'mt-1 w-full rounded-lg border border-red-400 px-3 py-2 focus:outline-none focus:ring-2 focus:ring-sqli-sky'

function validate(): boolean {
  titleError.value = ''
  departmentError.value = ''
  locationError.value = ''
  descriptionError.value = ''
  error.value = ''

  let valid = true
  if (!title.value.trim()) {
    titleError.value = 'Title is required.'
    valid = false
  }
  if (!department.value.trim()) {
    departmentError.value = 'Department is required.'
    valid = false
  }
  if (!location.value.trim()) {
    locationError.value = 'Location is required.'
    valid = false
  }
  if (!description.value.trim()) {
    descriptionError.value = 'Description is required.'
    valid = false
  }
  return valid
}

function buildPayload(): JobPayload {
  return {
    title: title.value.trim(),
    department: department.value.trim(),
    location: location.value.trim(),
    level: level.value,
    description: description.value.trim(),
    skills: skills.value,
    status: status.value,
  }
}

onMounted(async () => {
  if (!isEdit.value || !jobId.value) return

  pageLoading.value = true
  try {
    const job = await fetchJob(jobId.value)
    title.value = job.title
    department.value = job.department
    location.value = job.location
    level.value = job.level
    description.value = job.description
    skills.value = [...job.skills]
    status.value = job.status
  } catch {
    error.value = 'Could not load job for editing.'
  } finally {
    pageLoading.value = false
  }
})

async function handleSubmit() {
  if (!validate()) return

  loading.value = true
  try {
    const payload = buildPayload()
    if (isEdit.value && jobId.value) {
      await updateJob(jobId.value, payload)
      await router.push({
        name: 'job-detail',
        params: { id: jobId.value },
        query: { toast: 'Job updated successfully' },
      })
    } else {
      const job = await createJob(payload)
      await router.push({
        name: 'jobs',
        query: { toast: `Job "${job.title}" created successfully` },
      })
    }
  } catch (err: unknown) {
    error.value = axios.isAxiosError(err) && err.response?.status === 403
      ? 'Only recruiters can create or edit jobs.'
      : 'Could not save job. Please check the form and try again.'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AppLayout>
    <router-link
      :to="isEdit ? `/jobs/${jobId}` : '/jobs'"
      class="text-sm text-sqli-cobalt hover:underline mb-4 inline-block"
    >
      ← {{ isEdit ? 'Back to job' : 'Back to jobs' }}
    </router-link>

    <h1 class="text-2xl font-semibold text-sqli-midnight mb-6">
      {{ isEdit ? 'Edit job' : 'Create job' }}
    </h1>

    <p v-if="pageLoading" class="text-gray-500">Loading…</p>

    <form
      v-else
      class="bg-white rounded-xl border border-sqli-gray-100 p-8 max-w-2xl"
      @submit.prevent="handleSubmit"
    >
      <label class="block mb-4">
        <span class="text-sm text-gray-600">Title</span>
        <input v-model="title" type="text" :class="titleError ? inputErrorClass : inputClass" />
        <p v-if="titleError" class="text-red-500 text-sm mt-1">{{ titleError }}</p>
      </label>

      <div class="grid grid-cols-2 gap-4 mb-4">
        <label class="block">
          <span class="text-sm text-gray-600">Department</span>
          <input
            v-model="department"
            type="text"
            :class="departmentError ? inputErrorClass : inputClass"
          />
          <p v-if="departmentError" class="text-red-500 text-sm mt-1">{{ departmentError }}</p>
        </label>
        <label class="block">
          <span class="text-sm text-gray-600">Location</span>
          <input
            v-model="location"
            type="text"
            :class="locationError ? inputErrorClass : inputClass"
          />
          <p v-if="locationError" class="text-red-500 text-sm mt-1">{{ locationError }}</p>
        </label>
      </div>

      <div class="grid grid-cols-2 gap-4 mb-4">
        <label class="block">
          <span class="text-sm text-gray-600">Level</span>
          <select v-model="level" :class="inputClass">
            <option value="junior">Junior</option>
            <option value="mid">Mid</option>
            <option value="senior">Senior</option>
            <option value="lead">Lead</option>
          </select>
        </label>
        <label class="block">
          <span class="text-sm text-gray-600">Status</span>
          <select v-model="status" :class="inputClass">
            <option value="open">Open</option>
            <option value="on_hold">On hold</option>
            <option value="closed">Closed</option>
          </select>
        </label>
      </div>

      <label class="block mb-4">
        <span class="text-sm text-gray-600">Description</span>
        <textarea
          v-model="description"
          rows="5"
          :class="descriptionError ? inputErrorClass : inputClass"
        />
        <p v-if="descriptionError" class="text-red-500 text-sm mt-1">{{ descriptionError }}</p>
      </label>

      <label class="block mb-6">
        <span class="text-sm text-gray-600">Required skills</span>
        <SkillsTagInput v-model="skills" />
      </label>

      <p v-if="error" class="text-red-500 text-sm mb-4">{{ error }}</p>

      <div class="flex gap-3">
        <button
          type="submit"
          :disabled="loading"
          class="bg-sqli-cobalt hover:bg-[#003399] text-white font-medium px-6 py-2.5 rounded-lg disabled:opacity-50"
        >
          {{ loading ? 'Saving…' : isEdit ? 'Save changes' : 'Create job' }}
        </button>
        <router-link
          :to="isEdit ? `/jobs/${jobId}` : '/jobs'"
          class="px-6 py-2.5 rounded-lg border border-gray-200 text-gray-600 hover:bg-gray-50"
        >
          Cancel
        </router-link>
      </div>
    </form>
  </AppLayout>
</template>
