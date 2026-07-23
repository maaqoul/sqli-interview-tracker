export interface DashboardStats {
  open_jobs: number
  total_candidates: number
  interviews_this_week: number
  avg_time_to_hire: number | null
  ai_usage: {
    questions: number
    summary: number
    mock: number
    total: number
  }
  upcoming_interviews: {
    id: number
    scheduled_at: string
    type: string
    candidate_name: string
    job_title: string
  }[]
}

export interface FunnelStage {
  stage: string
  count: number
  color: string
}

export interface ActivityItem {
  id: number
  action_type: string
  description: string
  candidate_id: number
  candidate_name: string
  user_name: string | null
  created_at: string
}
