import api from '@/api/client'
import type { NotificationItem } from '@/types/notifications'

export async function fetchNotifications() {
  const { data } = await api.get<NotificationItem[] | { results: NotificationItem[] }>(
    '/api/notifications/',
  )
  if (Array.isArray(data)) return data
  return data.results ?? []
}

export async function fetchUnreadCount() {
  const { data } = await api.get<{ count: number }>('/api/notifications/unread-count/')
  return data.count
}

export async function markNotificationRead(id: number) {
  const { data } = await api.post<NotificationItem>(`/api/notifications/${id}/mark-read/`)
  return data
}

export async function markAllNotificationsRead() {
  const { data } = await api.post<{ updated: number }>('/api/notifications/mark-all-read/')
  return data
}
