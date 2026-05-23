import { computed, ref } from "vue";
import { adminPayoutAction, listAdminPayouts, type AdminPayoutRow } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

export type PayoutOpsRow = {
  id: string;
  creator: string;
  amount: number;
  status: "pending" | "processing" | "paid" | "failed";
  transfer_state: "queued" | "in_transit" | "completed" | "error";
};

function mapRow(row: AdminPayoutRow): PayoutOpsRow {
  return {
    id: row.id,
    creator: row.creator,
    amount: typeof row.amount === "number" ? row.amount : Number(row.amount),
    status: (["pending", "processing", "paid", "failed"].includes(row.status) ? row.status : "processing") as PayoutOpsRow["status"],
    transfer_state: (["queued", "in_transit", "completed", "error"].includes(row.transfer_state) ? row.transfer_state : "queued") as PayoutOpsRow["transfer_state"]
  };
}

export function usePayoutOps() {
  const loading = ref(true);
  const error = ref("");
  const query = ref("");
  const rows = ref<PayoutOpsRow[]>([]);
  const practitionerIds = ref<Record<string, string>>({});

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    if (!q) return rows.value;
    return rows.value.filter((row) => row.creator.toLowerCase().includes(q) || row.id.toLowerCase().includes(q));
  });

  async function load() {
    if (!sessionState.token) return;
    loading.value = true;
    error.value = "";
    try {
      const nextRows = await listAdminPayouts(sessionState.token, query.value);
      practitionerIds.value = Object.fromEntries(nextRows.map((row) => [row.id, row.practitioner_id]));
      rows.value = nextRows.map(mapRow);
    } catch (err) {
      error.value = `Failed payout ops: ${String(err)}`;
      showToast(error.value, "error");
    } finally {
      loading.value = false;
    }
  }

  async function markPaid(id: string) {
    if (!sessionState.token) return;
    const practitionerId = practitionerIds.value[id];
    if (!practitionerId) return;
    try {
      const updated = await adminPayoutAction(sessionState.token, practitionerId, "mark_paid");
      const ix = rows.value.findIndex((item) => item.id === id);
      if (ix >= 0) rows.value[ix] = mapRow(updated);
      showToast("Payout marked as paid.", "success");
    } catch (err) {
      showToast(`Mark paid failed: ${String(err)}`, "error");
    }
  }

  async function retryPayout(id: string) {
    if (!sessionState.token) return;
    const practitionerId = practitionerIds.value[id];
    if (!practitionerId) return;
    try {
      const updated = await adminPayoutAction(sessionState.token, practitionerId, "retry");
      const ix = rows.value.findIndex((item) => item.id === id);
      if (ix >= 0) rows.value[ix] = mapRow(updated);
      showToast("Payout retry queued.", "success");
    } catch (err) {
      showToast(`Retry failed: ${String(err)}`, "error");
    }
  }

  return { error, filtered, load, loading, markPaid, query, retryPayout, rows };
}
