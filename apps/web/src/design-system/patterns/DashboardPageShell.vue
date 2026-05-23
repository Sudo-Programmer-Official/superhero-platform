<template>
  <section class="page-shell">
    <header class="page-shell__header">
      <div class="page-shell__heading">
        <p v-if="eyebrow" class="page-shell__eyebrow">{{ eyebrow }}</p>
        <h1>{{ title }}</h1>
        <p v-if="subtitle" class="page-shell__subtitle">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="page-shell__actions">
        <slot name="actions" />
      </div>
    </header>

    <div class="page-shell__body">
      <slot />
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string;
  subtitle?: string;
  eyebrow?: string;
}>();
</script>

<style scoped>
.page-shell {
  width: 100%;
  max-width: 1280px;
  margin: 0 auto;
  padding: 24px 24px 32px;
  display: grid;
  gap: 24px;
}

.page-shell__header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
}

.page-shell__heading h1 {
  margin: 0;
  font-size: clamp(30px, 3vw, 40px);
  line-height: 1.1;
  letter-spacing: -0.02em;
}

.page-shell__eyebrow {
  margin: 0 0 12px;
  font-size: 12px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.58);
}

.page-shell__subtitle {
  margin: 12px 0 0;
  max-width: 72ch;
  color: rgba(255, 255, 255, 0.68);
  font-size: 15px;
}

.page-shell__actions {
  display: flex;
  align-items: center;
  gap: 12px;
}

.page-shell__body {
  display: grid;
  gap: 24px;
}

@media (max-width: 1023px) {
  .page-shell {
    padding: 20px 20px 24px;
  }

  .page-shell__header {
    gap: 20px;
    flex-direction: column;
  }

  .page-shell__actions {
    width: 100%;
  }
}

@media (max-width: 767px) {
  .page-shell {
    padding: 16px 16px 24px;
    gap: 20px;
  }
}
</style>
