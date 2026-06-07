<template>
  <div class="table-wrap">
    <div v-if="showToolbar" class="table-toolbar">
      <div class="table-toolbar__meta">
        <span>{{ visibleRows.length }} rows</span>
        <span v-if="props.selectable && selectedKeys.length > 0">{{ selectedKeys.length }} selected</span>
      </div>
      <div class="table-toolbar__actions">
        <slot name="bulk-actions" :selected-keys="selectedKeys" />
      </div>
    </div>
    <table class="table" :class="{ 'table--dense': props.dense }">
      <thead>
        <tr>
          <th v-if="props.selectable" class="check-col">
            <input
              type="checkbox"
              :checked="allVisibleSelected"
              :indeterminate.prop="isIndeterminate"
              @change="toggleAllVisible(($event.target as HTMLInputElement).checked)"
            />
          </th>
          <th v-for="column in props.columns" :key="column.key">{{ column.label }}</th>
        </tr>
      </thead>
      <tbody v-if="visibleRows.length > 0">
        <tr v-for="(row, rowIndex) in visibleRows" :key="props.rowKey(row, rowIndex)">
          <td v-if="props.selectable" class="check-col">
            <input type="checkbox" :checked="selectedSet.has(props.rowKey(row, rowIndex))" @change="toggleRow(row, rowIndex, ($event.target as HTMLInputElement).checked)" />
          </td>
          <td v-for="column in props.columns" :key="`${props.rowKey(row, rowIndex)}-${column.key}`">
            <slot :name="`cell-${column.key}`" :row="row" :value="row[column.key]">
              {{ row[column.key] }}
            </slot>
          </td>
        </tr>
      </tbody>
      <tbody v-else>
        <tr>
          <td :colspan="props.columns.length + (props.selectable ? 1 : 0)" class="empty-cell">
            <slot name="empty">No data found.</slot>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="props.pagination && totalPages > 1" class="pagination">
      <button :disabled="page <= 1" @click="page = page - 1">Previous</button>
      <span>Page {{ page }} / {{ totalPages }}</span>
      <button :disabled="page >= totalPages" @click="page = page + 1">Next</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";

type RowValue = Record<string, string | number | boolean | null | undefined>;

const props = withDefaults(
  defineProps<{
    columns: Array<{ key: string; label: string }>;
    rows: RowValue[];
    rowKey?: (row: RowValue, index: number) => string;
    dense?: boolean;
    selectable?: boolean;
    pagination?: boolean;
    pageSize?: number;
  }>(),
  {
    rowKey: (_row: RowValue, index: number) => String(index),
    dense: false,
    selectable: false,
    pagination: true,
    pageSize: 10
  }
);

const emit = defineEmits<{
  (e: "selection-change", keys: string[]): void;
}>();

const page = ref(1);
const selectedSet = ref(new Set<string>());

const safeRows = computed(() => (Array.isArray(props.rows) ? props.rows : []));
const totalPages = computed(() => Math.max(1, Math.ceil(safeRows.value.length / props.pageSize)));
const visibleRows = computed(() => {
  if (!props.pagination) return safeRows.value;
  const start = (page.value - 1) * props.pageSize;
  return safeRows.value.slice(start, start + props.pageSize);
});
const visibleKeys = computed(() => visibleRows.value.map((row, index) => props.rowKey(row, index)));
const selectedKeys = computed(() => [...selectedSet.value]);
const allVisibleSelected = computed(
  () => visibleKeys.value.length > 0 && visibleKeys.value.every((key) => selectedSet.value.has(key))
);
const isIndeterminate = computed(
  () => visibleKeys.value.some((key) => selectedSet.value.has(key)) && !allVisibleSelected.value
);
const showToolbar = computed(() => props.selectable || safeRows.value.length > 0);

watch(
  safeRows,
  () => {
    if (page.value > totalPages.value) page.value = totalPages.value;
    selectedSet.value = new Set<string>();
    emit("selection-change", []);
  }
);

watch(page, () => {
  if (page.value < 1) page.value = 1;
  if (page.value > totalPages.value) page.value = totalPages.value;
});

function toggleRow(row: RowValue, index: number, checked: boolean) {
  const key = props.rowKey(row, index);
  const next = new Set(selectedSet.value);
  if (checked) next.add(key);
  else next.delete(key);
  selectedSet.value = next;
  emit("selection-change", [...next]);
}

function toggleAllVisible(checked: boolean) {
  const next = new Set(selectedSet.value);
  for (const key of visibleKeys.value) {
    if (checked) next.add(key);
    else next.delete(key);
  }
  selectedSet.value = next;
  emit("selection-change", [...next]);
}
</script>

<style scoped>
.table-wrap {
  overflow: auto;
  margin-top: var(--space-16);
}
.table-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: var(--space-12);
  margin-bottom: var(--space-12);
}
.table-toolbar__meta {
  display: flex;
  gap: var(--space-12);
  color: rgba(255, 255, 255, 0.68);
  font-size: var(--type-label-small);
  letter-spacing: 0.06em;
  text-transform: uppercase;
}
.table-toolbar__actions {
  display: flex;
  gap: var(--space-8);
}

.table {
  width: 100%;
  min-width: 860px;
  border-collapse: collapse;
}

.table th {
  text-align: left;
  font-size: var(--type-label-small);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: rgba(255, 255, 255, 0.58);
  border-bottom: 1px solid rgba(255, 255, 255, 0.12);
  padding: var(--space-12);
}
.check-col {
  width: 40px;
}
.check-col input {
  width: 14px;
  height: 14px;
}

.table td {
  padding: var(--space-12);
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.table--dense th,
.table--dense td {
  padding-top: var(--space-10);
  padding-bottom: var(--space-10);
}

.empty-cell {
  text-align: center;
  color: rgba(255, 255, 255, 0.62);
  padding: var(--space-24);
}
.pagination {
  margin-top: var(--space-12);
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: var(--space-8);
}
.pagination button {
  min-height: 32px;
  padding: 0 10px;
  border-radius: 8px;
  border: 1px solid rgba(255, 255, 255, 0.18);
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.84);
}
.pagination button:disabled {
  opacity: 0.45;
}
.pagination span {
  color: rgba(255, 255, 255, 0.68);
  font-size: 12px;
}
</style>
