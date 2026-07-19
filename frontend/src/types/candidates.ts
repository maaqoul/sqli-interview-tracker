export type CandidateSource = 'linkedin' | 'referral' | 'job_board' | 'other' | ''
export type CandidateStatus = 'active' | 'rejected' | 'hired'

export interface Candidate {
  id: number
  first_name: string
  last_name: string
  email: string
  phone: string
  linkedin: string
  resume_file: string | null
  source: CandidateSource
  job: number
  job_title: string
  current_stage: number
  current_stage_name: string
  current_stage_color: string
  status: CandidateStatus
  created_at: string
  updated_at: string
}

export interface CandidatePayload {
  first_name: string
  last_name: string
  email: string
  phone?: string
  linkedin?: string
  source?: CandidateSource
  job: number
  current_stage?: number
}

export interface PaginatedCandidates {
  count: number
  next: string | null
  previous: string | null
  results: Candidate[]
}

export interface CandidateFilters {
  job_id?: number
  stage?: number
  search?: string
  page?: number
}

export interface MoveStagePayload {
  stage_id: number
  reason: string
}
