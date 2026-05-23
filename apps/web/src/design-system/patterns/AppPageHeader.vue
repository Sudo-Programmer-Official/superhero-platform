<template>
  <header class="page-header">
    <div class="page-header__heading">
      <p v-if="eyebrow" class="page-header__eyebrow">{{ eyebrow }}</p>
      <h1>{{ title }}</h1>
      <p v-if="subtitle" class="page-header__subtitle">{{ subtitle }}</p>
    </div>
    <div v-if="$slots.actions" class="page-header__actions">
      <slot name="actions" />
    </div>
  </header>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
  eyebrow?: string;
}>();
</script>

<style scoped>
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: var(--space-16);
}

.page-header__heading h1 {
  margin: 0;
  font-size: var(--type-page-title);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.page-header__eyebrow {
  margin: 0 0 var(--space-12);
  font-size: var(--type-label-small);
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.58);
}

.page-header__subtitle {
  margin: var(--space-12) 0 0;
  max-width: 72ch;
  color: rgba(255, 255, 255, 0.68);
  font-size: var(--type-body-muted);
  line-height: 1.45;
}

.page-header__actions {
  display: flex;
  align-items: center;
  gap: var(--space-12);
}

@media (max-width: 1023px) {
  .page-header {
    gap: var(--space-20);
    flex-direction: column;
  }

  .page-header__actions {
    width: 100%;
  }
}
</style>
