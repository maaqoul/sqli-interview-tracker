import api from '@/api/client'
import type { ActivityItem, DashboardStats, FunnelStage } from '@/types/dashboard'

export async function fetchDashboardStats() {
  const { data } = await api.get<DashboardStats>('/api/dashboard/stats/')
  return data
}

export async function fetchDashboardFunnel() {
  const { data } = await api.get<FunnelStage[]>('/api/dashboard/funnel/')
  return data
}

export async function fetchDashboardActivity() {
  const { data } = await api.get<{ count: number; results: ActivityItem[] }>(
    '/api/dashboard/activity/',
  )
  return data
}
