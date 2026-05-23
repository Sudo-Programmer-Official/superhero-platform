<template>
  <section class="page-shell">
    <AppPageHeader :eyebrow="eyebrow" :title="title" :subtitle="subtitle">
      <template v-if="$slots.actions" #actions>
        <slot name="actions" />
      </template>
    </AppPageHeader>

    <div class="page-shell__body">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
import AppPageHeader from "./AppPageHeader.vue";

defineProps<{
  title: string;
  subtitle?: string;
  eyebrow?: string;
}>();
</script>

<style scoped>
.page-shell {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: var(--space-page-y) var(--space-page-x) var(--space-page-bottom);
  display: grid;
  gap: var(--space-section);
}

.page-shell__body {
  display: grid;
  gap: var(--space-section);
}
</style>
