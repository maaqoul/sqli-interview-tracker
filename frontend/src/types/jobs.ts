export type JobLevel = 'junior' | 'mid' | 'senior' | 'lead'
export type JobStatus = 'open' | 'closed' | 'on_hold'

export interface Job {
  id: number
  title: string
  department: string
  location: string
  level: JobLevel
  description: string
  skills: string[]
  status: JobStatus
  created_by: number | null
  created_by_name: string | null
  created_at: string
}

export interface JobPayload {
  title: string
  department: string
  location: string
  level: JobLevel
  description: string
  skills: string[]
  status: JobStatus
}

export interface PaginatedJobs {
  count: number
  next: string | null
  previous: string | null
  results: Job[]
}

export interface PipelineStage {
  id: number
  name: string
  order: number
  color: string
}
