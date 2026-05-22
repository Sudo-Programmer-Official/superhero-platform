<template>
  <BaseGlassCard :muted="muted" padding="sm" radius="md" :class="cardClass">
    <slot />
  </BaseGlassCard>
</template>

<script setup lang="ts">
import { computed } from "vue";
import BaseGlassCard from "./BaseGlassCard.vue";

const props = withDefaults(
  defineProps<{
    muted?: boolean;
  }>(),
  {
    muted: false
  }
);

const cardClass = computed(
  () => "transition-transform duration-[var(--motion-fast)] ease-[var(--ease-standard)] hover:-translate-y-1"
);
</script>
