<template>
  <BaseInput
    :model-value="modelValue"
    :type="type"
    :placeholder="placeholder"
    :icon="icon"
    @update:modelValue="$emit('update:modelValue', $event)"
  />
</template>

<script setup lang="ts">
import BaseInput from "./BaseInput.vue";

defineProps<{
  modelValue: string | number;
  type?: string;
  placeholder?: string;
  icon?: string;
}>();

defineEmits<{
  "update:modelValue": [value: string];
}>();
</script>
