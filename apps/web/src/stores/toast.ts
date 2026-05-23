import { computed, reactive } from "vue";

export type ToastTone = "success" | "error" | "warning" | "info" | "loading";

export type ToastItem = {
  id: string;
  message: string;
  tone: ToastTone;
  durationMs: number;
};

const state = reactive({
  items: [] as ToastItem[]
});

function createId() {
  return `toast_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function showToast(message: string, tone: ToastTone = "info", durationMs = 2600): string {
  const id = createId();
  const item: ToastItem = { id, message, tone, durationMs };
  state.items.push(item);
  if (durationMs > 0) {
    window.setTimeout(() => dismissToast(id), durationMs);
  }
  return id;
}

export function dismissToast(id: string) {
  const ix = state.items.findIndex((item) => item.id === id);
  if (ix >= 0) state.items.splice(ix, 1);
}

export function clearToasts() {
  state.items.splice(0, state.items.length);
}

export function useToast() {
  return {
    items: computed(() => state.items),
    showToast,
    dismissToast,
    clearToasts
  };
}
