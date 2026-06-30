import api from '@/api/client'
import type { Job, JobPayload, PaginatedJobs, PipelineStage } from '@/types/jobs'

export async function fetchJobs(status?: string) {
  const { data } = await api.get<PaginatedJobs>('/api/jobs/', {
    params: status ? { status } : undefined,
  })
  return data
}

export async function fetchJob(id: number) {
  const { data } = await api.get<Job>(`/api/jobs/${id}/`)
  return data
}

export async function createJob(payload: JobPayload) {
  const { data } = await api.post<Job>('/api/jobs/', payload)
  return data
}

export async function updateJob(id: number, payload: Partial<JobPayload>) {
  const { data } = await api.patch<Job>(`/api/jobs/${id}/`, payload)
  return data
}

export async function fetchJobStages(id: number) {
  const { data } = await api.get<PipelineStage[]>(`/api/jobs/${id}/stages/`)
  return data
}
