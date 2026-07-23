import api from '@/api/client'
import type {
  GenerateQuestionsPayload,
  GenerateQuestionsResponse,
  HiringBrief,
  MockInterviewPayload,
  MockInterviewResponse,
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
