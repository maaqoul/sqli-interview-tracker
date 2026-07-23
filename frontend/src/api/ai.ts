import api from '@/api/client'
import type {
  AISession,
  AISessionType,
  GenerateQuestionsPayload,
  GenerateQuestionsResponse,
  HiringBrief,
  MockInterviewPayload,
  MockInterviewResponse,
  PaginatedAISessions,
} from '@/types/ai'

export async function generateQuestions(payload: GenerateQuestionsPayload) {
  const { data } = await api.post<GenerateQuestionsResponse>(
    '/api/ai/generate-questions/',
    payload,
  )
  return data
}

export async function summarizeFeedback(candidateId: number) {
  const { data } = await api.post<HiringBrief>('/api/ai/summarize-feedback/', {
    candidate_id: candidateId,
  })
  return data
}

export async function mockInterviewTurn(payload: MockInterviewPayload) {
  const { data } = await api.post<MockInterviewResponse>(
    '/api/ai/mock-interview/',
    payload,
  )
  return data
}

export async function fetchAISessions(type?: AISessionType | '') {
  const { data } = await api.get<PaginatedAISessions>('/api/ai/sessions/', {
    params: type ? { type } : undefined,
  })
  return data
}

export async function fetchAISession(id: number) {
  const { data } = await api.get<AISession>(`/api/ai/sessions/${id}/`)
  return data
}
