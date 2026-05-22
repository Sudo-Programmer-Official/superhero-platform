<template>
  <BaseButton
    :to="to"
    :tag="tag"
    :type="type"
    :variant="variant"
    :size="size"
    :context="context"
    :disabled="disabled"
  >
    <slot />
  </BaseButton>
</template>

<script setup lang="ts">
import BaseButton from "./BaseButton.vue";

withDefaults(
  defineProps<{
    to?: string;
    tag?: "button" | "a" | "RouterLink";
    type?: "button" | "submit" | "reset";
    variant?: "primary" | "secondary" | "ghost";
    size?: "sm" | "md" | "lg" | "nav" | "form";
    context?: "default" | "navbar";
    disabled?: boolean;
  }>(),
  {
    tag: "button",
    type: "button",
    variant: "ghost",
    size: "md",
    context: "default",
    disabled: false
  }
);
</script>
