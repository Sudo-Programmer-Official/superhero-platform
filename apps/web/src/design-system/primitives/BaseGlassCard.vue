<template>
  <article :class="cardClass">
    <slot />
  </article>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
  defineProps<{
    muted?: boolean;
    padding?: "sm" | "md" | "lg";
    radius?: "md" | "lg";
    variant?: "default" | "auth";
  }>(),
  {
    muted: false,
    padding: "md",
    radius: "lg",
    variant: "default"
  }
);

const cardClass = computed(() => {
  if (props.variant === "auth") {
    const authBase =
      "rounded-[32px] border border-[rgba(255,255,255,0.08)] bg-[rgba(10,14,28,0.72)] backdrop-blur-[24px] shadow-[0_24px_80px_rgba(0,0,0,0.45)]";
    return props.muted ? `${authBase} opacity-85` : authBase;
  }

  const pad = props.padding === "lg" ? "p-6 md:p-8" : props.padding === "sm" ? "p-5 md:p-6" : "p-6 md:p-7";
  const rad = props.radius === "md" ? "rounded-[24px]" : "rounded-[28px]";
  const base =
    `${rad} border border-[rgba(255,255,255,0.10)] bg-[rgba(12,16,28,0.72)] ${pad} backdrop-blur-[24px] shadow-[0_26px_70px_rgba(0,0,0,0.52),0_10px_34px_rgba(0,0,0,0.24),inset_0_1px_0_rgba(255,255,255,0.16)]`;
  return props.muted ? `${base} opacity-85` : base;
});
</script>
