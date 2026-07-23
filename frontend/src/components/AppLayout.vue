<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const STORAGE_KEY = 'sqli_sidebar_collapsed'
const collapsed = ref(false)
const mobileOpen = ref(false)

const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  const a = (u.first_name?.[0] || '').toUpperCase()
  const b = (u.last_name?.[0] || '').toUpperCase()
  return (a + b) || u.email[0]?.toUpperCase() || '?'
})

const navItems = computed(() => {
  const items = [
    { to: '/dashboard', label: 'Dashboard', match: '/dashboard' },
    { to: '/candidates', label: 'Candidates', match: '/candidates' },
    { to: '/jobs', label: 'Jobs', match: '/jobs' },
    { to: '/interviews', label: 'Interviews', match: '/interviews' },
    { to: '/my-interviews', label: 'My Interviews', match: '/my-interviews' },
    { to: '/ai', label: 'AI Tools', match: '/ai' },
    { to: '/settings', label: 'Settings', match: '/settings' },
  ]
  if (auth.user?.role === 'admin') {
    items.splice(2, 0, { to: '/register', label: 'Create user', match: '/register' })
  }
  return items
})

function isActive(match: string) {
  return route.path === match || route.path.startsWith(match + '/')
}

function toggleCollapsed() {
  collapsed.value = !collapsed.value
  localStorage.setItem(STORAGE_KEY, collapsed.value ? '1' : '0')
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}

function syncViewport() {
  if (window.innerWidth < 1024) {
    collapsed.value = true
  }
}

watch(
  () => route.path,
  () => {
    mobileOpen.value = false
  },
)

onMounted(() => {
  const saved = localStorage.getItem(STORAGE_KEY)
  if (saved === '1') collapsed.value = true
  syncViewport()
  window.addEventListener('resize', syncViewport)
})

onUnmounted(() => {
  window.removeEventListener('resize', syncViewport)
})
</script>

<template>
  <div class="min-h-screen flex bg-sqli-cream">
    <!-- Mobile overlay -->
    <div
      v-if="mobileOpen"
      class="fixed inset-0 bg-black/40 z-30 lg:hidden"
      @click="mobileOpen = false"
    />

    <!-- Sidebar -->
    <aside
      class="bg-sqli-midnight text-white flex flex-col shrink-0 transition-all duration-200 z-40
             fixed lg:static inset-y-0 left-0"
      :class="[
        collapsed ? 'w-16' : 'w-64',
        mobileOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0',
      ]"
    >
      <div class="p-4 flex items-center gap-3 min-h-[56px]" :class="collapsed ? 'justify-center' : ''">
        <div class="text-lg font-bold tracking-wide shrink-0">SQLI</div>
        <p v-if="!collapsed" class="text-sqli-sky text-xs leading-tight">Interview Tracker</p>
      </div>

      <nav class="flex-1 px-2 space-y-1 text-sm overflow-y-auto">
        <router-link
          v-for="item in navItems"
          :key="item.to"
          :to="item.to"
          class="flex items-center gap-3 rounded-lg transition-colors relative"
          :class="[
            collapsed ? 'justify-center px-2 py-2.5' : 'px-3 py-2.5',
            isActive(item.match)
              ? 'bg-white/10 text-white'
              : 'text-white/60 hover:text-white hover:bg-white/5',
          ]"
          :title="collapsed ? item.label : undefined"
        >
          <span
            v-if="isActive(item.match)"
            class="absolute left-0 top-1/2 -translate-y-1/2 w-[3px] h-5 bg-sqli-sky rounded-r"
          />
          <!-- Simple letter mark when collapsed; label when expanded -->
          <span
            v-if="collapsed"
            class="w-7 h-7 rounded-md bg-white/10 flex items-center justify-center text-xs font-semibold"
          >
            {{ item.label[0] }}
          </span>
          <span v-else>{{ item.label }}</span>
        </router-link>
      </nav>

      <div class="p-3 border-t border-white/10">
        <button
          type="button"
          class="w-full text-xs text-white/50 hover:text-white py-2 rounded-lg hover:bg-white/5"
          :title="collapsed ? 'Expand' : 'Collapse'"
          @click="toggleCollapsed"
        >
          {{ collapsed ? '»' : '« Collapse' }}
        </button>
      </div>
    </aside>

    <!-- Main column -->
    <div class="flex-1 flex flex-col min-w-0 min-h-screen">
      <!-- Topbar -->
      <header
        class="h-14 bg-white border-b border-sqli-gray-100 flex items-center justify-between px-4 lg:px-6 shrink-0"
      >
        <button
          type="button"
          class="lg:hidden text-sqli-midnight text-sm px-2 py-1 rounded-lg border border-gray-200"
          @click="mobileOpen = !mobileOpen"
        >
          Menu
        </button>
        <div class="hidden lg:block text-sm text-gray-400 truncate">
          {{ auth.user?.email }}
        </div>

        <div class="flex items-center gap-3 ml-auto">
          <!-- Notification bell placeholder (INT-041) -->
          <button
            type="button"
            class="relative w-9 h-9 rounded-full border border-gray-200 text-gray-500 hover:bg-sqli-cream flex items-center justify-center disabled:opacity-60"
            title="Notifications (coming in INT-041)"
            disabled
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
              <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
            </svg>
          </button>

          <div
            class="flex items-center gap-2 pl-2 border-l border-gray-100"
            :title="`${auth.user?.first_name} ${auth.user?.last_name}`"
          >
            <div
              class="w-9 h-9 rounded-full bg-sqli-cobalt text-white text-sm font-semibold flex items-center justify-center"
            >
              {{ initials }}
            </div>
            <div class="hidden sm:block text-left leading-tight mr-1">
              <p class="text-sm text-sqli-midnight font-medium truncate max-w-[140px]">
                {{ auth.user?.first_name }} {{ auth.user?.last_name }}
              </p>
              <p class="text-xs text-gray-400 capitalize">{{ auth.user?.role }}</p>
            </div>
            <button
              type="button"
              class="text-sm text-gray-500 hover:text-sqli-midnight px-2"
              @click="handleLogout"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main class="flex-1 p-6 lg:p-8">
        <slot />
      </main>
    </div>
  </div>
</template>
