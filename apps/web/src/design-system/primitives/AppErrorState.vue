<template>
  <div class="error-state" role="alert">
    <h4>{{ title }}</h4>
    <p>{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
withDefaults(
  defineProps<{
    title?: string;
    description: string;
  }>(),
  {
    title: "Something went wrong"
  }
);
</script>

<style scoped>
.error-state {
  border-radius: 14px;
  border: 1px solid rgba(255, 120, 120, 0.42);
  background: rgba(110, 24, 24, 0.18);
  color: #ffd4d4;
  padding: var(--space-card);
  display: grid;
  gap: var(--space-12);
}

.error-state h4 {
  margin: 0;
  font-size: var(--type-section-title);
  line-height: 1.1;
}

.error-state p {
  margin: 0;
  color: rgba(255, 220, 220, 0.88);
}
</style>
