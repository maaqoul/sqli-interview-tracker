import api from '@/api/client'
import type {
  PaginatedScorecards,
  Scorecard,
  ScorecardPayload,
} from '@/types/scorecards'

export async function fetchScorecards(params: {
  interview_id?: number
  candidate_id?: number
} = {}) {
  const { data } = await api.get<PaginatedScorecards | Scorecard[]>('/api/scorecards/', {
    params,
  })
  if (Array.isArray(data)) {
    return { count: data.length, next: null, previous: null, results: data }
  }
  return data
}

export async function fetchScorecard(id: number) {
  const { data } = await api.get<Scorecard>(`/api/scorecards/${id}/`)
  return data
}

export async function submitScorecard(payload: ScorecardPayload) {
  const { data } = await api.post<Scorecard>('/api/scorecards/', payload)
  return data
}
