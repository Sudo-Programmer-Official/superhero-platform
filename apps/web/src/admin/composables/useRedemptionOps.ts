import { computed, ref } from "vue";
import { listAdminRedemptions, type AdminRedemptionRow } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

export type RedemptionOpsRow = {
  wallet_pass_id: string;
  deal_title: string | null;
  practitioner_name: string | null;
  attendee_email: string | null;
  success_count: number;
  failed_count: number;
  duplicate_attempts: number;
  invalid_attempts: number;
  last_event_at: string;
  risk_level: string;
};

function mapRow(row: AdminRedemptionRow): RedemptionOpsRow {
  return {
    wallet_pass_id: row.wallet_pass_id,
    deal_title: row.deal_title,
    practitioner_name: row.practitioner_name,
    attendee_email: row.attendee_email,
    success_count: row.success_count,
    failed_count: row.failed_count,
    duplicate_attempts: row.duplicate_attempts,
    invalid_attempts: row.invalid_attempts,
    last_event_at: row.last_event_at,
    risk_level: row.risk_level
  };
}

export function useRedemptionOps() {
  const loading = ref(true);
  const error = ref("");
  const query = ref("");
  const window = ref<"24h" | "7d" | "30d" | "all">("24h");
  const rows = ref<RedemptionOpsRow[]>([]);

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    if (!q) return rows.value;
    return rows.value.filter(
      (row) =>
        row.wallet_pass_id.toLowerCase().includes(q) ||
        (row.deal_title || "").toLowerCase().includes(q) ||
        (row.practitioner_name || "").toLowerCase().includes(q) ||
        (row.attendee_email || "").toLowerCase().includes(q)
    );
  });

  async function load() {
    if (!sessionState.token) return;
    loading.value = true;
    error.value = "";
    try {
      rows.value = (await listAdminRedemptions(sessionState.token, query.value, window.value)).map(mapRow);
    } catch (err) {
      error.value = `Failed redemption ops: ${String(err)}`;
      showToast(error.value, "error");
    } finally {
      loading.value = false;
    }
  }

  return { error, filtered, load, loading, query, rows, window };
}
