import { computed, ref } from "vue";
import { listAdminWalletPasses, type AdminWalletPassRow } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

export type WalletPassOpsRow = {
  id: string;
  deal_title: string;
  practitioner_name: string;
  attendee_email: string | null;
  booking_number: string | null;
  pass_status: string;
  redemption_status: string;
  wallet_type: string;
  source_checkout_session_id: string | null;
  qr_code: string;
  created_at: string;
};

function mapRow(row: AdminWalletPassRow): WalletPassOpsRow {
  return {
    id: row.id,
    deal_title: row.deal_title,
    practitioner_name: row.practitioner_name,
    attendee_email: row.attendee_email,
    booking_number: row.booking_number,
    pass_status: row.pass_status,
    redemption_status: row.redemption_status,
    wallet_type: row.wallet_type,
    source_checkout_session_id: row.source_checkout_session_id,
    qr_code: row.qr_code,
    created_at: row.created_at
  };
}

export function useWalletPassOps() {
  const loading = ref(true);
  const error = ref("");
  const query = ref("");
  const rows = ref<WalletPassOpsRow[]>([]);

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    if (!q) return rows.value;
    return rows.value.filter(
      (row) =>
        row.deal_title.toLowerCase().includes(q) ||
        row.practitioner_name.toLowerCase().includes(q) ||
        (row.attendee_email || "").toLowerCase().includes(q) ||
        (row.booking_number || "").toLowerCase().includes(q) ||
        row.qr_code.toLowerCase().includes(q)
    );
  });

  async function load() {
    if (!sessionState.token) return;
    loading.value = true;
    error.value = "";
    try {
      rows.value = (await listAdminWalletPasses(sessionState.token, query.value)).map(mapRow);
    } catch (err) {
      error.value = `Failed wallet pass ops: ${String(err)}`;
      showToast(error.value, "error");
    } finally {
      loading.value = false;
    }
  }

  return { error, filtered, load, loading, query, rows };
}
