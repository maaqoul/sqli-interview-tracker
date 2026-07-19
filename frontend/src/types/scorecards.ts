export type Recommendation = 'strong_yes' | 'yes' | 'neutral' | 'no' | 'strong_no'

export interface SkillRatings {
  technical: number
  communication: number
  problem_solving: number
  culture_fit: number
  leadership: number
}

export interface Scorecard {
  id: number
  interview: number
  interview_type: string
  interviewer: number
  interviewer_name: string
  candidate_name: string
  overall_rating: number
  skill_ratings: SkillRatings
  strengths: string
  weaknesses: string
  recommendation: Recommendation
  private_notes?: string
  submitted_at: string
}

export interface ScorecardPayload {
  interview: number
  overall_rating: number
  skill_ratings: SkillRatings
  strengths?: string
  weaknesses?: string
  recommendation: Recommendation
  private_notes?: string
}

export interface PaginatedScorecards {
  count: number
  next: string | null
  previous: string | null
  results: Scorecard[]
}

export const SKILL_LABELS: Record<keyof SkillRatings, string> = {
  technical: 'Technical',
  communication: 'Communication',
  problem_solving: 'Problem Solving',
  culture_fit: 'Culture Fit',
  leadership: 'Leadership',
}

export const RECOMMENDATION_OPTIONS: { value: Recommendation; label: string }[] = [
  { value: 'strong_yes', label: 'Strong Yes' },
  { value: 'yes', label: 'Yes' },
  { value: 'neutral', label: 'Neutral' },
  { value: 'no', label: 'No' },
  { value: 'strong_no', label: 'Strong No' },
]
