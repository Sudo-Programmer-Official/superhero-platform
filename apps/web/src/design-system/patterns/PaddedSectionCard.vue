<template>
  <AppCard :muted="muted" class="section-card">
    <slot />
  </AppCard>
</template>

<script setup lang="ts">
import AppCard from "../primitives/AppCard.vue";

withDefaults(
  defineProps<{
    muted?: boolean;
  }>(),
  {
    muted: false
  }
);
</script>

<style scoped>
.section-card {
  padding: var(--space-card-header-top) var(--space-card) var(--space-card);
}
</style>
