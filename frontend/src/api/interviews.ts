import api from '@/api/client'
import type {
  Interview,
  InterviewFilters,
  InterviewPayload,
  PaginatedInterviews,
} from '@/types/interviews'

export async function fetchInterviews(filters: InterviewFilters = {}) {
  const { data } = await api.get<PaginatedInterviews>('/api/interviews/', {
    params: {
      date_from: filters.date_from,
      date_to: filters.date_to,
      interviewer: filters.interviewer,
      status: filters.status,
      candidate_id: filters.candidate_id,
    },
  })
  return data
}

export async function fetchInterview(id: number) {
  const { data } = await api.get<Interview>(`/api/interviews/${id}/`)
  return data
}

export async function createInterview(payload: InterviewPayload) {
  const { data } = await api.post<Interview>('/api/interviews/', payload)
  return data
}

export async function updateInterview(id: number, payload: Partial<InterviewPayload>) {
  const { data } = await api.patch<Interview>(`/api/interviews/${id}/`, payload)
  return data
}

export async function fetchAssignableUsers(role?: string) {
  const { data } = await api.get<
    | { id: number; email: string; first_name: string; last_name: string; role: string }[]
    | { results: { id: number; email: string; first_name: string; last_name: string; role: string }[] }
  >('/api/auth/users/', {
    params: role ? { role } : undefined,
  })
  if (Array.isArray(data)) return data
  return data.results ?? []
}
