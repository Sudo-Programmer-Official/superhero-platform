<template>
  <section :class="sectionClass">
    <slot />
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    compact?: boolean;
  }>(),
  { compact: false }
);

const sectionClass = computed(() =>
  props.compact ? "py-12" : "py-[96px]"
);
</script>
