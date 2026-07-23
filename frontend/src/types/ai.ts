export type QuestionType = 'technical' | 'behavioral'
export type QuestionDifficulty = 'easy' | 'medium' | 'hard'

export interface InterviewQuestion {
  question: string
  type: QuestionType
  difficulty: QuestionDifficulty
}

export interface GenerateQuestionsPayload {
  job_id?: number | null
  job_title: string
  level: string
  skills: string[]
  interview_type: string
  n?: number
  save?: boolean
}

export interface GenerateQuestionsResponse {
  questions: InterviewQuestion[]
  count: number
  session_id: number | null
}
