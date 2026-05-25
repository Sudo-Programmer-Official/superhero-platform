import { computed, ref } from "vue";
import { listAdminBookings, type AdminBookingRow } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

export type BookingOpsRow = {
  id: string;
  booking_number: string;
  deal_title: string;
  practitioner_name: string;
  customer_email: string;
  quantity: number;
  total_amount: number;
  currency: string;
  payment_status: string;
  redemption_status: string;
  created_at: string;
};

function mapRow(row: AdminBookingRow): BookingOpsRow {
  return {
    id: row.id,
    booking_number: row.booking_number,
    deal_title: row.deal_title,
    practitioner_name: row.practitioner_name,
    customer_email: row.customer_email,
    quantity: row.quantity,
    total_amount: typeof row.total_amount === "number" ? row.total_amount : Number(row.total_amount),
    currency: row.currency,
    payment_status: row.payment_status,
    redemption_status: row.redemption_status,
    created_at: row.created_at
  };
}

export function useBookingOps() {
  const loading = ref(true);
  const error = ref("");
  const query = ref("");
  const rows = ref<BookingOpsRow[]>([]);

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    if (!q) return rows.value;
    return rows.value.filter(
      (row) =>
        row.booking_number.toLowerCase().includes(q) ||
        row.customer_email.toLowerCase().includes(q) ||
        row.deal_title.toLowerCase().includes(q) ||
        row.practitioner_name.toLowerCase().includes(q)
    );
  });

  async function load() {
    if (!sessionState.token) return;
    loading.value = true;
    error.value = "";
    try {
      rows.value = (await listAdminBookings(sessionState.token, query.value)).map(mapRow);
    } catch (err) {
      error.value = `Failed booking ops: ${String(err)}`;
      showToast(error.value, "error");
    } finally {
      loading.value = false;
    }
  }

  return { error, filtered, load, loading, query, rows };
}
