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

export interface HiringBrief {
  strengths: string[]
  concerns: string[]
  recommendation: string
  suggested_next_step: string
  session_id: number
  scorecard_count: number
  notes_count: number
  disclaimer: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
}

export interface MockInterviewPayload {
  role: string
  level: string
  history: ChatMessage[]
  user_answer?: string
  session_id?: number | null
  end?: boolean
}

export interface MockInterviewResponse {
  feedback: string
  next_question: string
  done: boolean
  summary: string
  history: ChatMessage[]
  session_id: number
}
