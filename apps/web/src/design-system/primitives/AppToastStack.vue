<template>
  <div class="toast-stack" aria-live="polite" aria-atomic="true">
    <transition-group name="toast-fade">
      <article v-for="item in items" :key="item.id" class="toast" :data-tone="item.tone">
        <p>{{ item.message }}</p>
        <button type="button" @click="dismissToast(item.id)">Dismiss</button>
      </article>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { useToast } from "../../stores/toast";

const { items, dismissToast } = useToast();
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
}

.toast[data-tone="error"] {
  border-color: rgba(255, 120, 120, 0.5);
}

.toast[data-tone="warning"] {
  border-color: rgba(248, 209, 143, 0.48);
}

.toast[data-tone="loading"] {
  border-color: rgba(130, 165, 255, 0.42);
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
</style>
