import { computed, ref } from "vue";

export type ModerationItem = {
  id: string;
  entity: "deal" | "practitioner" | "media";
  reason: string;
  severity: "low" | "medium" | "high";
  state: "open" | "in_review" | "resolved";
};

const items = Array.from({ length: 16 }).map((_, index) => ({
  id: `mod-${index + 1}`,
  entity: (["deal", "practitioner", "media"] as const)[index % 3],
  reason: ["reported content", "duplicate listing", "fraud signal", "spam behavior"][index % 4],
  severity: (["low", "medium", "high"] as const)[index % 3],
  state: (["open", "in_review", "resolved"] as const)[index % 3]
}));

export function useModerationCenter() {
  const query = ref("");
  const rows = ref(items);

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    if (!q) return rows.value;
    return rows.value.filter((item) => item.reason.toLowerCase().includes(q) || item.entity.includes(q));
  });

  function resolve(id: string) {
    const row = rows.value.find((item) => item.id === id);
    if (!row) return;
    row.state = "resolved";
  }

  return { filtered, query, resolve, rows };
}
