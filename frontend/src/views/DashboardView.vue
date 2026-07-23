<script setup lang="ts">
import {
  BarElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  Title,
  Tooltip,
} from 'chart.js'
import { computed, onMounted, ref } from 'vue'
import { Bar } from 'vue-chartjs'
import { useRouter } from 'vue-router'
import {
  fetchDashboardActivity,
  fetchDashboardFunnel,
  fetchDashboardStats,
} from '@/api/dashboard'
import AppLayout from '@/components/AppLayout.vue'
import type { ActivityItem, DashboardStats, FunnelStage } from '@/types/dashboard'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

const router = useRouter()

const stats = ref<DashboardStats | null>(null)
const funnel = ref<FunnelStage[]>([])
const activity = ref<ActivityItem[]>([])
const loading = ref(true)
const error = ref('')

const chartData = computed(() => ({
  labels: funnel.value.map((f) => f.stage),
  datasets: [
    {
      label: 'Candidates',
      data: funnel.value.map((f) => f.count),
      backgroundColor: funnel.value.map((f) => f.color),
      borderRadius: 4,
      barThickness: 18,
    },
  ],
}))

const chartOptions = {
  indexAxis: 'y' as const,
  responsive: true,
  maintainAspectRatio: false,
  plugins: {
    legend: { display: false },
    tooltip: { enabled: true },
  },
  scales: {
    x: {
      beginAtZero: true,
      ticks: { precision: 0 },
      grid: { color: '#F3F4F6' },
    },
    y: {
      grid: { display: false },
    },
  },
}

function relativeTime(iso: string) {
  const diff = Date.now() - new Date(iso).getTime()
  const mins = Math.floor(diff / 60000)
  if (mins < 1) return 'just now'
  if (mins < 60) return `${mins}m ago`
  const hours = Math.floor(mins / 60)
  if (hours < 24) return `${hours}h ago`
  const days = Math.floor(hours / 24)
  return `${days}d ago`
}

function formatInterviewWhen(iso: string) {
  return new Date(iso).toLocaleString('en-GB', {
    weekday: 'short',
    hour: '2-digit',
    minute: '2-digit',
  })
}

onMounted(async () => {
  loading.value = true
  error.value = ''
  try {
    const [s, f, a] = await Promise.all([
      fetchDashboardStats(),
      fetchDashboardFunnel(),
      fetchDashboardActivity(),
    ])
    stats.value = s
    funnel.value = f
    activity.value = a.results
  } catch {
    error.value = 'Could not load dashboard data.'
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <AppLayout>
    <h1 class="text-2xl font-semibold text-sqli-midnight mb-1">Dashboard</h1>
    <p class="text-gray-500 text-sm mb-6">Overview of your hiring pipeline</p>

    <p v-if="loading" class="text-sm text-gray-500">Loading…</p>
    <p v-else-if="error" class="text-sm text-red-600">{{ error }}</p>

    <template v-else-if="stats">
      <!-- Stat cards -->
      <div class="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4 mb-6">
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <p class="text-sm text-gray-500">Open Jobs</p>
          <p class="text-3xl font-bold text-sqli-cobalt mt-1">{{ stats.open_jobs }}</p>
        </div>
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <p class="text-sm text-gray-500">Total Candidates</p>
          <p class="text-3xl font-bold text-sqli-cobalt mt-1">{{ stats.total_candidates }}</p>
        </div>
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <p class="text-sm text-gray-500">Interviews This Week</p>
          <p class="text-3xl font-bold text-sqli-cobalt mt-1">
            {{ stats.interviews_this_week }}
          </p>
        </div>
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <p class="text-sm text-gray-500">Avg Time-to-Hire</p>
          <p class="text-3xl font-bold text-sqli-cobalt mt-1">
            {{ stats.avg_time_to_hire != null ? `${stats.avg_time_to_hire}d` : '—' }}
          </p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <!-- Funnel -->
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <h2 class="font-medium text-sqli-midnight mb-4">Pipeline Funnel</h2>
          <div class="h-64">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
        </div>

        <!-- Activity -->
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <h2 class="font-medium text-sqli-midnight mb-4">Recent Activity</h2>
          <ul v-if="activity.length" class="space-y-3 max-h-64 overflow-y-auto">
            <li
              v-for="item in activity"
              :key="item.id"
              class="flex gap-3 text-sm cursor-pointer hover:bg-sqli-cream/60 rounded-lg p-1 -mx-1"
              @click="router.push(`/candidates/${item.candidate_id}`)"
            >
              <div
                class="w-8 h-8 rounded-full bg-sqli-cream text-sqli-cobalt text-xs font-semibold flex items-center justify-center shrink-0"
              >
                {{ item.candidate_name.slice(0, 1) }}
              </div>
              <div class="min-w-0 flex-1">
                <p class="text-sqli-midnight truncate">{{ item.description }}</p>
                <p class="text-xs text-gray-400 mt-0.5">
                  {{ item.candidate_name }} · {{ relativeTime(item.created_at) }}
                </p>
              </div>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500">No recent activity.</p>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- AI usage -->
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <h2 class="font-medium text-sqli-midnight mb-4">AI Usage</h2>
          <div class="grid grid-cols-2 gap-3 text-sm">
            <div class="rounded-lg bg-sqli-cream/60 p-3">
              <p class="text-gray-500 text-xs">Questions</p>
              <p class="text-xl font-semibold text-sqli-midnight mt-0.5">
                {{ stats.ai_usage.questions }}
              </p>
            </div>
            <div class="rounded-lg bg-sqli-cream/60 p-3">
              <p class="text-gray-500 text-xs">Summaries</p>
              <p class="text-xl font-semibold text-sqli-midnight mt-0.5">
                {{ stats.ai_usage.summary }}
              </p>
            </div>
            <div class="rounded-lg bg-sqli-cream/60 p-3">
              <p class="text-gray-500 text-xs">Mock sessions</p>
              <p class="text-xl font-semibold text-sqli-midnight mt-0.5">
                {{ stats.ai_usage.mock }}
              </p>
            </div>
            <div class="rounded-lg bg-sqli-cream/60 p-3">
              <p class="text-gray-500 text-xs">Total</p>
              <p class="text-xl font-semibold text-sqli-midnight mt-0.5">
                {{ stats.ai_usage.total }}
              </p>
            </div>
          </div>
        </div>

        <!-- Upcoming interviews -->
        <div class="bg-white rounded-xl p-6 border border-sqli-gray-100">
          <h2 class="font-medium text-sqli-midnight mb-4">Upcoming Interviews</h2>
          <ul v-if="stats.upcoming_interviews.length" class="space-y-2 text-sm">
            <li
              v-for="iv in stats.upcoming_interviews"
              :key="iv.id"
              class="flex justify-between gap-3 border-b border-sqli-gray-100 last:border-0 pb-2 last:pb-0"
            >
              <div>
                <p class="text-sqli-midnight font-medium">{{ iv.candidate_name }}</p>
                <p class="text-xs text-gray-500 capitalize">
                  {{ iv.job_title }} · {{ iv.type }}
                </p>
              </div>
              <p class="text-xs text-gray-400 whitespace-nowrap">
                {{ formatInterviewWhen(iv.scheduled_at) }}
              </p>
            </li>
          </ul>
          <p v-else class="text-sm text-gray-500">No interviews remaining this week.</p>
        </div>
      </div>
    </template>
  </AppLayout>
</template>
