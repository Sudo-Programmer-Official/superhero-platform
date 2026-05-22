<template>
  <div :class="orbClass" aria-hidden="true"></div>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    tone?: "violet" | "gold";
    size?: "md" | "lg";
    position?: string;
  }>(),
  {
    tone: "violet",
    size: "lg",
    position: ""
  }
);

const orbClass = computed(() => {
  const toneClass = props.tone === "gold" ? "bg-[var(--accent-glow)]" : "bg-[var(--brand-violet-glow)]";
  const sizeClass = props.size === "md" ? "h-56 w-56" : "h-80 w-80";
  return `pointer-events-none absolute rounded-full blur-[72px] ${toneClass} ${sizeClass} ${props.position}`;
});
</script>
