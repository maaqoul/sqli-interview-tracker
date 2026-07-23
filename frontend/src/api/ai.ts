import api from '@/api/client'
import type {
  GenerateQuestionsPayload,
  GenerateQuestionsResponse,
} from '@/types/ai'

export async function generateQuestions(payload: GenerateQuestionsPayload) {
  const { data } = await api.post<GenerateQuestionsResponse>(
    '/api/ai/generate-questions/',
    payload,
  )
  return data
}
