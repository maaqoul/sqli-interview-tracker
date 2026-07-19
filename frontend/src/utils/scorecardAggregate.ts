import type { Recommendation, Scorecard, SkillRatings } from '@/types/scorecards'
import { RECOMMENDATION_OPTIONS, SKILL_LABELS } from '@/types/scorecards'

const YES_RECS: Recommendation[] = ['strong_yes', 'yes']

export interface ScorecardAggregate {
  count: number
  averageOverall: number | null
  averageSkills: Partial<Record<keyof SkillRatings, number>>
  yesCount: number
  consensusLabel: string
  breakdown: { value: Recommendation; label: string; count: number }[]
}

function round1(n: number) {
  return Math.round(n * 10) / 10
}

export function aggregateScorecards(scorecards: Scorecard[]): ScorecardAggregate {
  const count = scorecards.length
  if (!count) {
    return {
      count: 0,
      averageOverall: null,
      averageSkills: {},
      yesCount: 0,
      consensusLabel: 'No scorecards yet',
      breakdown: [],
    }
  }

  const averageOverall = round1(
    scorecards.reduce((sum, s) => sum + s.overall_rating, 0) / count,
  )

  const averageSkills: Partial<Record<keyof SkillRatings, number>> = {}
  for (const key of Object.keys(SKILL_LABELS) as (keyof SkillRatings)[]) {
    const vals = scorecards
      .map((s) => s.skill_ratings?.[key])
      .filter((v): v is number => typeof v === 'number')
    if (vals.length) {
      averageSkills[key] = round1(vals.reduce((a, b) => a + b, 0) / vals.length)
    }
  }

  const yesCount = scorecards.filter((s) => YES_RECS.includes(s.recommendation)).length
  const consensusLabel = `${yesCount}/${count} recommend Yes`

  const counts = new Map<Recommendation, number>()
  for (const s of scorecards) {
    counts.set(s.recommendation, (counts.get(s.recommendation) ?? 0) + 1)
  }
  const breakdown = RECOMMENDATION_OPTIONS.map((opt) => ({
    value: opt.value,
    label: opt.label,
    count: counts.get(opt.value) ?? 0,
  })).filter((row) => row.count > 0)

  return {
    count,
    averageOverall,
    averageSkills,
    yesCount,
    consensusLabel,
    breakdown,
  }
}

export function recommendationLabel(value: Recommendation) {
  return RECOMMENDATION_OPTIONS.find((o) => o.value === value)?.label ?? value
}

export function starsDisplay(rating: number) {
  const full = Math.round(rating)
  return '★'.repeat(full) + '☆'.repeat(Math.max(0, 5 - full))
}
