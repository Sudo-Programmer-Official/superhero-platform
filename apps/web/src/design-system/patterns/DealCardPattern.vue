<template>
  <AppCard>
    <p class="mb-1 text-xs uppercase tracking-[0.12em] text-[var(--text-muted)]"><slot name="meta" /></p>
    <p class="m-0 text-base font-semibold leading-snug text-[var(--text-primary)]"><slot name="title" /></p>
    <p v-if="$slots.subtitle" class="mt-2 text-sm text-[var(--text-1)]"><slot name="subtitle" /></p>
    <p v-if="$slots.price" class="mt-3 text-xl font-semibold text-[var(--accent)]"><slot name="price" /></p>
    <div v-if="$slots.actions" class="mt-3 grid gap-2"><slot name="actions" /></div>
  </AppCard>
</template>

<script setup lang="ts">
import AppCard from "../primitives/AppCard.vue";
</script>
