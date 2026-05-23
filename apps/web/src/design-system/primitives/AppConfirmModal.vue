<template>
  <div v-if="open" class="modal-backdrop" @click.self="$emit('cancel')">
    <section class="modal" role="dialog" aria-modal="true" :aria-label="title">
      <p class="eyebrow">Confirm Action</p>
      <h3>{{ title }}</h3>
      <p>{{ description }}</p>
      <div class="actions">
        <AppButton variant="ghost" size="sm" @click="$emit('cancel')">Cancel</AppButton>
        <AppButton variant="secondary" size="sm" @click="$emit('confirm')">{{ confirmLabel }}</AppButton>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import AppButton from "./AppButton.vue";

defineProps<{ open: boolean; title: string; description: string; confirmLabel?: string }>();
defineEmits<{ (e: "cancel"): void; (e: "confirm"): void }>();
</script>

<style scoped>
.modal-backdrop { position: fixed; inset: 0; z-index: 70; background: rgba(4,7,16,.58); backdrop-filter: blur(3px); display: grid; place-items: center; padding: 16px; }
.modal { width: min(460px, 100%); border-radius: 14px; border: 1px solid rgba(255,255,255,.14); background: linear-gradient(160deg, rgba(17,24,42,.95), rgba(10,16,30,.95)); padding: 18px; display: grid; gap: 10px; }
.eyebrow { margin: 0; font-size: 11px; text-transform: uppercase; letter-spacing: .1em; color: rgba(255,255,255,.6); }
h3 { margin: 0; font-size: 20px; }
p { margin: 0; color: rgba(255,255,255,.72); }
.actions { display: flex; justify-content: flex-end; gap: 8px; margin-top: 8px; }
</style>
