<template>
  <div class="empty-state">
    <h4>{{ title }}</h4>
    <p>{{ description }}</p>
    <slot />
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  description: string;
}>();
</script>

<style scoped>
.empty-state {
  border-radius: 14px;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  background: rgba(255, 255, 255, 0.02);
  padding: var(--space-card);
  display: grid;
  gap: var(--space-12);
  text-align: center;
}

.empty-state h4 {
  margin: 0;
  font-size: var(--type-section-title);
  line-height: 1.15;
}

.empty-state p {
  margin: 0;
  color: rgba(255, 255, 255, 0.65);
}
</style>
