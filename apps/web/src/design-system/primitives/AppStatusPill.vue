<template>
  <span class="status-pill" :data-tone="config.tone">{{ config.label }}</span>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { getStatusConfig } from "../../shared/constants/statusRegistry";

const props = defineProps<{ status: string }>();
const config = computed(() => getStatusConfig(props.status));
</script>

<style scoped>
.status-pill {
  display: inline-flex;
  align-items: center;
  min-height: 24px;
  padding: 0 10px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  font-size: var(--type-label-small);
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.88);
  background: rgba(255, 255, 255, 0.04);
}

.status-pill[data-tone="success"] {
  color: #45e8b0;
  border-color: rgba(69, 232, 176, 0.4);
  background: rgba(69, 232, 176, 0.1);
}

.status-pill[data-tone="warning"] {
  color: #f8d18f;
  border-color: rgba(248, 209, 143, 0.4);
  background: rgba(248, 209, 143, 0.12);
}

.status-pill[data-tone="danger"] {
  color: #ff9fa6;
  border-color: rgba(255, 159, 166, 0.4);
  background: rgba(255, 159, 166, 0.1);
}

.status-pill[data-tone="info"] {
  color: #a8c7ff;
  border-color: rgba(168, 199, 255, 0.4);
  background: rgba(168, 199, 255, 0.1);
}
</style>
