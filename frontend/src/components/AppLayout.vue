<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

function isActive(path: string) {
  return route.path === path || route.path.startsWith(path + '/')
}

function handleLogout() {
  auth.logout()
  router.push('/login')
}
</script>

<template>
  <div class="min-h-screen flex">
    <aside class="w-64 bg-sqli-midnight text-white p-6 flex flex-col shrink-0">
      <div class="text-xl font-bold mb-1">SQLI</div>
      <p class="text-sqli-sky text-xs mb-8">Interview Tracker</p>
      <nav class="space-y-2 text-sm flex-1">
        <router-link
          to="/dashboard"
          class="block px-3 py-2 rounded-lg transition-colors"
          :class="isActive('/dashboard') ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'"
        >
          Dashboard
        </router-link>
        <router-link
          to="/jobs"
          class="block px-3 py-2 rounded-lg transition-colors"
          :class="isActive('/jobs') ? 'bg-white/10 text-white' : 'text-white/60 hover:text-white hover:bg-white/5'"
        >
          Jobs
        </router-link>
        <router-link
          v-if="auth.user?.role === 'admin'"
          to="/register"
          class="block px-3 py-2 rounded-lg text-white/60 hover:text-white hover:bg-white/5"
        >
          Create user
        </router-link>
        <span class="block px-3 py-2 rounded-lg text-white/40 cursor-not-allowed">Candidates</span>
        <span class="block px-3 py-2 rounded-lg text-white/40 cursor-not-allowed">Interviews</span>
        <span class="block px-3 py-2 rounded-lg text-white/40 cursor-not-allowed">AI Tools</span>
      </nav>
      <div class="text-xs text-white/50 mb-2 truncate">
        {{ auth.user?.first_name }} {{ auth.user?.last_name }}
      </div>
      <button class="text-sm text-white/70 hover:text-white text-left" @click="handleLogout">
        Logout
      </button>
    </aside>

    <main class="flex-1 p-8 bg-sqli-cream min-h-screen">
      <slot />
    </main>
  </div>
</template>
