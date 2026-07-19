export type InterviewType = 'phone' | 'video' | 'onsite'
export type InterviewStatus = 'scheduled' | 'completed' | 'cancelled' | 'no_show'

export interface Interview {
  id: number
  candidate: number
  candidate_name: string
  job: number
  job_title: string
  type: InterviewType
  scheduled_at: string
  duration_min: number
  location: string
  video_link: string
  status: InterviewStatus
  interviewer_ids: number[]
  interviewer_names: string[]
  created_by: number | null
  created_by_name: string | null
  created_at: string
}

export interface InterviewPayload {
  candidate: number
  job: number
  type: InterviewType
  scheduled_at: string
  duration_min: number
  location?: string
  video_link?: string
  status?: InterviewStatus
  interviewer_ids: number[]
}

export interface PaginatedInterviews {
  count: number
  next: string | null
  previous: string | null
  results: Interview[]
}

export interface InterviewFilters {
  date_from?: string
  date_to?: string
  interviewer?: number
  status?: string
  candidate_id?: number
}

export const INTERVIEW_TYPE_COLORS: Record<InterviewType, string> = {
  phone: '#6EC4E8',
  video: '#0047BB',
  onsite: '#001B44',
}

export const INTERVIEW_TYPE_LABELS: Record<InterviewType, string> = {
  phone: 'Phone',
  video: 'Video',
  onsite: 'Onsite',
}
