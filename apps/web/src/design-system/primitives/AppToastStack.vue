<template>
  <div class="toast-stack" aria-live="polite" aria-atomic="true">
    <transition-group name="toast-fade">
      <article v-for="item in items" :key="item.id" class="toast" :data-tone="item.tone">
        <div class="toast__content">
          <span class="toast__icon">{{ toneIcon(item.tone) }}</span>
          <p>{{ item.message }}</p>
        </div>
        <button type="button" @click="dismissToast(item.id)">Dismiss</button>
      </article>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { useToast, type ToastTone } from "../../stores/toast";

const { items, dismissToast } = useToast();

function toneIcon(tone: ToastTone): string {
  if (tone === "success") return "✓";
  if (tone === "error") return "!";
  if (tone === "warning") return "!";
  if (tone === "loading") return "…";
  return "i";
}
</script>

<style scoped>
.toast-stack {
  position: fixed;
  right: 18px;
  bottom: 18px;
  z-index: 120;
  display: grid;
  gap: 10px;
  max-width: min(420px, calc(100vw - 24px));
}

.toast {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(8, 14, 26, 0.92);
  color: #e8eef8;
  padding: 10px 12px;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 10px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.3);
}
.toast__content {
  display: flex;
  align-items: flex-start;
  gap: 10px;
}
.toast__icon {
  width: 20px;
  height: 20px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  border: 1px solid rgba(255,255,255,.2);
  color: rgba(255,255,255,.92);
  font-size: 12px;
  font-weight: 700;
  flex: 0 0 20px;
}

.toast p {
  margin: 0;
  font-size: 14px;
  line-height: 1.35;
}

.toast button {
  border: 0;
  padding: 0;
  color: rgba(255, 255, 255, 0.72);
  background: transparent;
  font-size: 12px;
  cursor: pointer;
}

.toast[data-tone="success"] {
  border-color: rgba(69, 232, 176, 0.42);
  box-shadow: 0 12px 28px rgba(18, 58, 44, 0.45);
}

.toast[data-tone="error"] {
  border-color: rgba(255, 120, 120, 0.5);
  box-shadow: 0 12px 28px rgba(77, 25, 25, 0.5);
}

.toast[data-tone="warning"] {
  border-color: rgba(248, 209, 143, 0.48);
  box-shadow: 0 12px 28px rgba(83, 58, 23, 0.44);
}

.toast[data-tone="loading"] {
  border-color: rgba(130, 165, 255, 0.42);
  box-shadow: 0 12px 28px rgba(31, 45, 79, 0.42);
}

.toast[data-tone="success"] .toast__icon {
  border-color: rgba(69, 232, 176, 0.5);
  color: #45e8b0;
}

.toast[data-tone="error"] .toast__icon {
  border-color: rgba(255, 120, 120, 0.6);
  color: #ff9fa6;
}

.toast[data-tone="warning"] .toast__icon {
  border-color: rgba(248, 209, 143, 0.6);
  color: #f8d18f;
}

.toast[data-tone="loading"] .toast__icon {
  border-color: rgba(130, 165, 255, 0.58);
  color: #a8c7ff;
  animation: spin 1.2s linear infinite;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
  transition: opacity 180ms ease, transform 180ms ease;
}

.toast-fade-enter-from,
.toast-fade-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
</style>
