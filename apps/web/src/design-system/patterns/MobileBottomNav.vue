<template>
  <nav class="fixed inset-x-4 bottom-[max(0.55rem,var(--safe-bottom))] z-30 grid grid-cols-3 gap-1 rounded-[1rem] border border-[color:var(--glass-border)] bg-[rgba(10,18,30,.72)] p-1.5 backdrop-blur-2xl shadow-[var(--shadow-glass)] lg:hidden" aria-label="Primary">
    <RouterLink class="rounded-md px-2 py-2 text-center text-xs text-[var(--text-secondary)] no-underline" :class="{ 'bg-[rgba(214,228,255,.14)] text-[var(--text-primary)]': route.name === 'dashboard' }" to="/dashboard">Home</RouterLink>
    <RouterLink class="rounded-md px-2 py-2 text-center text-xs text-[var(--text-secondary)] no-underline" :class="{ 'bg-[rgba(214,228,255,.14)] text-[var(--text-primary)]': route.name === 'deals' }" to="/dashboard/deals">Deals</RouterLink>
    <RouterLink class="rounded-md px-2 py-2 text-center text-xs text-[var(--text-secondary)] no-underline" :class="{ 'bg-[rgba(214,228,255,.14)] text-[var(--text-primary)]': route.name === 'profile' }" to="/dashboard/profile">Profile</RouterLink>
  </nav>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
const route = useRoute();
</script>
