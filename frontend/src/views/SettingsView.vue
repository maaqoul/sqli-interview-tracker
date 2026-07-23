<script setup lang="ts">
import AppLayout from '@/components/AppLayout.vue'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
</script>

<template>
  <AppLayout>
    <h1 class="text-2xl font-semibold text-sqli-midnight mb-2">Settings</h1>
    <p class="text-gray-500 text-sm mb-8">Profile and preferences</p>

    <div class="bg-white rounded-xl border border-sqli-gray-100 p-6 max-w-lg space-y-3 text-sm">
      <p>
        <span class="text-gray-400 text-xs uppercase">Name</span><br />
        {{ auth.user?.first_name }} {{ auth.user?.last_name }}
      </p>
      <p>
        <span class="text-gray-400 text-xs uppercase">Email</span><br />
        {{ auth.user?.email }}
      </p>
      <p>
        <span class="text-gray-400 text-xs uppercase">Role</span><br />
        <span class="capitalize">{{ auth.user?.role }}</span>
      </p>
      <p class="text-gray-500 pt-2 border-t border-sqli-gray-100">
        Edit profile, password, and admin user management come in INT-042.
      </p>
    </div>
  </AppLayout>
</template>
