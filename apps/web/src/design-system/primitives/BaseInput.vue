<template>
  <label class="base-input">
    <span v-if="icon" class="base-input__icon" aria-hidden="true">{{ icon }}</span>
    <input
      :value="modelValue"
      :type="type"
      :placeholder="placeholder"
      :class="['base-input__field', icon ? 'base-input__field--icon' : '']"
      @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
    />
  </label>
</template>

<script setup lang="ts">
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

<style scoped>
.base-input {
  position: relative;
  display: block;
  width: 100%;
}

.base-input__icon {
  position: absolute;
  top: 50%;
  left: 12px;
  display: grid;
  height: 28px;
  width: 28px;
  transform: translateY(-50%);
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.58);
  font-size: 13px;
  transition: all 180ms ease;
}

.base-input__field {
  height: 52px;
  width: 100%;
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.08), rgba(10, 18, 30, 0.84));
  padding-inline: 18px;
  color: var(--text-primary);
  font-size: 16px;
  font-weight: 500;
  letter-spacing: -0.01em;
  outline: none;
  backdrop-filter: blur(12px);
  transition: all 180ms ease;
}

.base-input__field::placeholder {
  color: rgba(255, 255, 255, 0.42);
}

.base-input__field--icon {
  padding-left: 52px;
}

.base-input:hover .base-input__field {
  border-color: rgba(255, 255, 255, 0.16);
}

.base-input:focus-within .base-input__field {
  border-color: rgba(255, 215, 120, 0.7);
  box-shadow: 0 0 0 4px rgba(255, 215, 120, 0.16), 0 10px 28px rgba(0, 0, 0, 0.28);
}

.base-input:hover .base-input__icon {
  border-color: rgba(255, 255, 255, 0.16);
  color: rgba(255, 255, 255, 0.76);
}

.base-input:focus-within .base-input__icon {
  border-color: rgba(255, 215, 120, 0.34);
  color: var(--accent);
}
</style>
