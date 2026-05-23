<template>
  <AppCard class="glass-panel" :muted="muted">
    <slot />
  </AppCard>
</template>

<script setup lang="ts">
import AppCard from "./AppCard.vue";

withDefaults(
  defineProps<{
    muted?: boolean;
  }>(),
  { muted: false }
);
</script>

<style scoped>
.glass-panel {
  padding: var(--space-card);
  border: 1px solid rgba(255, 255, 255, 0.12);
  box-shadow: 0 14px 34px rgba(2, 8, 28, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.16);
}
</style>
