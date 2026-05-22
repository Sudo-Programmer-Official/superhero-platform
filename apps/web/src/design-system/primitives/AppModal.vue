<template>
  <div v-if="open" class="fixed inset-0 z-50 grid place-items-center bg-[rgba(4,8,16,.58)] p-4 backdrop-blur-sm" @click.self="$emit('close')">
    <div class="w-full max-w-[560px] rounded-[1.4rem] border border-[color:var(--glass-border)] bg-[linear-gradient(145deg,var(--glass-bg),rgba(11,19,32,.92))] p-6 shadow-[var(--shadow-glass)]">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ open: boolean }>();
defineEmits<{ close: [] }>();
</script>
