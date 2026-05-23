import { computed, ref } from "vue";
import { adminDealAction, listAdminDeals, type AdminDealRow } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

export type DealOpsRow = {
  id: string;
  title: string;
  practitioner_name: string;
  status: "draft" | "published" | "expired" | "archived";
  moderation_state: "clean" | "flagged";
  revenue: number;
  bookings_count: number;
};

function mapRow(row: AdminDealRow): DealOpsRow {
  return {
    id: row.id,
    title: row.title,
    practitioner_name: row.practitioner_name,
    status: (["draft", "published", "expired", "archived"].includes(row.status) ? row.status : "draft") as DealOpsRow["status"],
    moderation_state: (["clean", "flagged"].includes(row.moderation_state) ? row.moderation_state : "clean") as DealOpsRow["moderation_state"],
    revenue: typeof row.revenue === "number" ? row.revenue : Number(row.revenue),
    bookings_count: row.bookings_count
  };
}

export function useDealOps() {
  const loading = ref(true);
  const error = ref("");
  const query = ref("");
  const rows = ref<DealOpsRow[]>([]);

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    if (!q) return rows.value;
    return rows.value.filter((row) => row.title.toLowerCase().includes(q) || row.practitioner_name.toLowerCase().includes(q));
  });

  async function load() {
    if (!sessionState.token) return;
    loading.value = true;
    error.value = "";
    try {
      rows.value = (await listAdminDeals(sessionState.token, query.value)).map(mapRow);
    } catch (err) {
      error.value = `Failed deal ops: ${String(err)}`;
      showToast(error.value, "error");
    } finally {
      loading.value = false;
    }
  }

  async function performAction(action: "archive" | "unpublish" | "feature" | "moderate", id: string) {
    if (!sessionState.token) return;
    try {
      const updated = await adminDealAction(sessionState.token, id, action);
      const ix = rows.value.findIndex((row) => row.id === id);
      if (ix >= 0) rows.value[ix] = mapRow(updated);
      showToast(`Deal action applied: ${action}`, "success");
    } catch (err) {
      showToast(`Deal action failed: ${String(err)}`, "error");
    }
  }

  return { error, filtered, load, loading, performAction, query, rows };
}
