import api from '@/api/client'
import type {
  Candidate,
  CandidateFilters,
  CandidatePayload,
  MoveStagePayload,
  PaginatedCandidates,
} from '@/types/candidates'

export async function fetchCandidates(filters: CandidateFilters = {}) {
  const { data } = await api.get<PaginatedCandidates>('/api/candidates/', {
    params: {
      job_id: filters.job_id,
      stage: filters.stage,
      search: filters.search || undefined,
      page: filters.page,
    },
  })
  return data
}

export async function fetchCandidate(id: number) {
  const { data } = await api.get<Candidate>(`/api/candidates/${id}/`)
  return data
}

export async function createCandidate(payload: CandidatePayload) {
  const { data } = await api.post<Candidate>('/api/candidates/', payload)
  return data
}

export async function moveCandidateStage(id: number, payload: MoveStagePayload) {
  const { data } = await api.post<Candidate>(`/api/candidates/${id}/move-stage/`, payload)
  return data
}
