<template>
  <div class="loading-state" role="status" aria-live="polite">
    <div class="spinner" aria-hidden="true"></div>
    <div class="copy">
      <h4>{{ title }}</h4>
      <p v-if="description">{{ description }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    description?: string;
  }>(),
  {
    title: "Loading…",
    description: ""
  }
);
</script>

<style scoped>
.loading-state {
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.03);
  padding: var(--space-card);
  display: flex;
  align-items: center;
  gap: var(--space-16);
}

.spinner {
  width: 22px;
  height: 22px;
  border-radius: 999px;
  border: 2px solid rgba(255, 255, 255, 0.22);
  border-top-color: rgba(240, 190, 100, 0.95);
  animation: spin 0.85s linear infinite;
  flex: 0 0 auto;
}

.copy h4 {
  margin: 0;
  font-size: 16px;
}

.copy p {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.66);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
