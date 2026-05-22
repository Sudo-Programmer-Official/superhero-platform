<template>
  <component
    :is="tag"
    :to="to"
    :type="tag === 'button' ? type : undefined"
    :class="buttonClass"
    :disabled="disabled"
  >
    <slot />
  </component>
</template>

<script setup lang="ts">
import { computed } from "vue";

const props = withDefaults(
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

const buttonClass = computed(() => [
  "btn",
  `btn--size-${props.size}`,
  `btn--variant-${props.variant}`,
  `btn--ctx-${props.context}`
]);
</script>

<style scoped>
.btn {
  box-sizing: border-box;
  display: inline-flex;
  flex-shrink: 0;
  align-items: center;
  justify-content: center;
  gap: 8px;
  white-space: nowrap;
  border: 1px solid transparent;
  border-radius: 16px;
  font-family: var(--font-sans);
  font-weight: 600;
  letter-spacing: -0.01em;
  line-height: 1;
  text-decoration: none;
  text-rendering: geometricPrecision;
  -webkit-font-smoothing: antialiased;
  transition: all 180ms ease;
}

.btn:active { transform: scale(0.98); }
.btn:disabled { cursor: not-allowed; opacity: 0.6; }

.btn--size-sm { min-height: 40px; padding-inline: 20px; font-size: 14px; }
.btn--size-md { min-height: 44px; padding-inline: 24px; font-size: 14px; }
.btn--size-lg { min-height: 56px; padding-inline: 28px; font-size: 15px; }
.btn--size-form { min-height: 48px; padding-inline: 24px; font-size: 15px; }
.btn--size-nav { min-height: 44px; min-width: 124px; padding-inline: 20px; font-size: 15px; }

.btn--ctx-navbar { border-radius: 999px; }

.btn--variant-primary {
  border-color: rgba(244, 201, 125, 0.82);
  background: linear-gradient(165deg, #f8da9f 0%, #e0b26c 42%, #c88d43 100%);
  color: #17120a;
  box-shadow: 0 14px 32px rgba(200, 141, 67, 0.42), 0 6px 18px rgba(0, 0, 0, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.btn--variant-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 18px 40px rgba(200, 141, 67, 0.52), 0 8px 22px rgba(0, 0, 0, 0.28), inset 0 1px 0 rgba(255, 255, 255, 0.62);
}

.btn--variant-secondary {
  border-color: var(--glass-border);
  background: var(--glass-bg);
  color: var(--text-primary);
  backdrop-filter: blur(12px);
  box-shadow: var(--shadow-glass);
}

.btn--variant-secondary:hover {
  transform: translateY(-2px);
  background: var(--glass-bg-strong);
}

.btn--variant-ghost {
  border-color: var(--glass-border);
  background: rgba(200, 220, 255, 0.08);
  color: var(--text-primary);
  backdrop-filter: blur(12px);
}

.btn--variant-ghost:hover { background: rgba(200, 220, 255, 0.16); }

.btn--ctx-navbar.btn--variant-secondary {
  border-color: rgba(255, 255, 255, 0.10);
  background: rgba(255, 255, 255, 0.04);
  color: var(--text-primary);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.10);
}

.btn--ctx-navbar.btn--variant-secondary:hover {
  transform: none;
  border-color: rgba(255, 255, 255, 0.16);
  background: rgba(255, 255, 255, 0.08);
}

.btn--ctx-navbar.btn--variant-primary {
  border-color: rgba(244, 201, 125, 0.86);
  background: linear-gradient(165deg, #f8da9f 0%, #e0b26c 44%, #c88d43 100%);
  color: #17120a;
  box-shadow: 0 8px 24px rgba(246, 197, 109, 0.18), 0 4px 12px rgba(0, 0, 0, 0.22), inset 0 1px 0 rgba(255, 255, 255, 0.55);
}

.btn--ctx-navbar.btn--variant-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 10px 28px rgba(246, 197, 109, 0.22), 0 6px 16px rgba(0, 0, 0, 0.24), inset 0 1px 0 rgba(255, 255, 255, 0.62);
}
</style>
