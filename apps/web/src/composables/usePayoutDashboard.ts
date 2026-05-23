import { computed, ref } from "vue";
import type { Booking } from "../domain/booking";
import { formatPayoutMoney, type Payout, type PayoutStatus, type PayoutTransaction } from "../domain/payout";
import { listBookings, listDeals } from "../services/api";
import { sessionState } from "../stores/session";

const PAGE_SIZE = 8;

function randomStatus(index: number): PayoutStatus {
  const statuses: PayoutStatus[] = ["paid", "pending", "processing", "paid", "paid", "failed", "refunded"];
  return statuses[index % statuses.length];
}

export function usePayoutDashboard() {
  const loading = ref(true);
  const error = ref("");
  const query = ref("");
  const statusFilter = ref<"all" | PayoutStatus>("all");
  const page = ref(1);
  const revenueTrend = ref<number[]>([]);
  const bookingsTrend = ref<number[]>([]);
  const payoutTrend = ref<number[]>([]);
  const payouts = ref<Payout[]>([]);
  const transactions = ref<PayoutTransaction[]>([]);
  const stripeState = ref({
    stripe_account_id: null as string | null,
    onboarding_state: "not_connected" as "not_connected" | "onboarding" | "connected" | "restricted",
    payouts_enabled: false,
    charges_enabled: false
  });

  const filteredTransactions = computed(() => {
    const q = query.value.trim().toLowerCase();
    return transactions.value.filter((item) => {
      if (statusFilter.value !== "all" && item.status !== statusFilter.value) return false;
      if (!q) return true;
      return (
        item.customer.toLowerCase().includes(q) ||
        item.deal.toLowerCase().includes(q) ||
        item.payout_batch.toLowerCase().includes(q)
      );
    });
  });

  const totalPages = computed(() => Math.max(1, Math.ceil(filteredTransactions.value.length / PAGE_SIZE)));

  const visibleTransactions = computed(() => {
    const start = (page.value - 1) * PAGE_SIZE;
    return filteredTransactions.value.slice(start, start + PAGE_SIZE);
  });

  const grossRevenue = computed(() => transactions.value.reduce((sum, item) => sum + item.gross, 0));
  const platformFees = computed(() => transactions.value.reduce((sum, item) => sum + item.platform_fees, 0));
  const stripeFees = computed(() => transactions.value.reduce((sum, item) => sum + item.stripe_fees, 0));
  const refunded = computed(() => transactions.value.filter((item) => item.status === "refunded").reduce((sum, item) => sum + item.gross, 0));
  const netRevenue = computed(() => transactions.value.reduce((sum, item) => sum + item.net, 0));

  const availableBalance = computed(() => payouts.value.filter((p) => p.payout_status === "pending").reduce((sum, p) => sum + p.amount, 0));
  const pendingPayouts = computed(() => payouts.value.filter((p) => p.payout_status === "processing").reduce((sum, p) => sum + p.amount, 0));
  const totalRevenue = computed(() => grossRevenue.value);

  const nextPayoutDate = computed(() => {
    const next = payouts.value.find((p) => p.payout_status === "pending" || p.payout_status === "processing");
    return next?.payout_date || null;
  });

  const stripeBadge = computed(() => {
    if (!stripeState.value.stripe_account_id) return { label: "Not connected", tone: "amber" as const, cta: "Connect Stripe" };
    if (!stripeState.value.payouts_enabled || !stripeState.value.charges_enabled) {
      return { label: "Verification needed", tone: "red" as const, cta: "Complete Verification" };
    }
    if (stripeState.value.onboarding_state === "restricted") return { label: "Restricted", tone: "red" as const, cta: "Manage Stripe" };
    return { label: "Connected", tone: "green" as const, cta: "Manage Stripe" };
  });

  function formatMoney(value: number) {
    return formatPayoutMoney(value, "USD");
  }

  function exportCsv() {
    const lines = ["customer,deal,gross,platform_fees,stripe_fees,net,status,payout_batch,created_at"];
    for (const item of filteredTransactions.value) {
      lines.push([
        item.customer,
        item.deal,
        item.gross.toFixed(2),
        item.platform_fees.toFixed(2),
        item.stripe_fees.toFixed(2),
        item.net.toFixed(2),
        item.status,
        item.payout_batch,
        item.created_at
      ].map((v) => `\"${String(v).replaceAll("\"", "\"\"")}\"`).join(","));
    }
    const blob = new Blob([lines.join("\n")], { type: "text/csv;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "openmat-payout-transactions.csv";
    a.click();
    URL.revokeObjectURL(url);
  }

  function goPrevPage() {
    page.value = Math.max(1, page.value - 1);
  }

  function goNextPage() {
    page.value = Math.min(totalPages.value, page.value + 1);
  }

  async function load() {
    loading.value = true;
    error.value = "";
    try {
      if (!sessionState.token) throw new Error("Authentication session expired.");
      const [bookings, deals] = await Promise.all([listBookings(sessionState.token), listDeals(sessionState.token)]);
      transactions.value = buildTransactions(bookings, deals.map((d) => d.title));
      payouts.value = buildPayouts(transactions.value, sessionState.me?.practitioner_id || "unknown");
      revenueTrend.value = aggregateTrend(transactions.value.map((t) => t.gross));
      bookingsTrend.value = aggregateTrend(transactions.value.map((t) => 1));
      payoutTrend.value = aggregateTrend(payouts.value.map((p) => p.amount));

      stripeState.value = {
        stripe_account_id: sessionState.me?.stripe_account_id || null,
        onboarding_state: sessionState.me?.onboarding_state || "not_connected",
        payouts_enabled: Boolean(sessionState.me?.payouts_enabled),
        charges_enabled: Boolean(sessionState.me?.charges_enabled)
      };
    } catch (err) {
      error.value = `Failed to load payouts dashboard: ${String(err)}`;
      transactions.value = [];
      payouts.value = [];
    } finally {
      loading.value = false;
    }
  }

  return {
    availableBalance,
    bookingsTrend,
    error,
    exportCsv,
    filteredTransactions,
    formatMoney,
    goNextPage,
    goPrevPage,
    grossRevenue,
    load,
    loading,
    netRevenue,
    nextPayoutDate,
    page,
    pendingPayouts,
    platformFees,
    payoutTrend,
    payouts,
    query,
    refunded,
    revenueTrend,
    statusFilter,
    stripeBadge,
    stripeFees,
    stripeState,
    totalPages,
    totalRevenue,
    transactions,
    visibleTransactions
  };
}

function buildTransactions(bookings: Booking[], dealNames: string[]): PayoutTransaction[] {
  return bookings.map((booking, index) => {
    const gross = Number(booking.total_amount || 0);
    const platform = Number((gross * 0.08).toFixed(2));
    const stripe = Number((gross * 0.029 + 0.3).toFixed(2));
    const net = Number((gross - platform - stripe).toFixed(2));
    return {
      id: booking.id,
      customer: booking.customer_name || booking.customer_email,
      deal: dealNames[index % Math.max(1, dealNames.length)] || `Deal ${booking.deal_id.slice(0, 6)}`,
      gross,
      platform_fees: platform,
      stripe_fees: stripe,
      net,
      status: booking.payment_status as PayoutStatus,
      payout_batch: `BATCH-${String(index + 1).padStart(4, "0")}`,
      created_at: booking.created_at
    };
  });
}

function buildPayouts(transactions: PayoutTransaction[], practitionerId: string): Payout[] {
  const groups: Payout[] = [];
  for (let i = 0; i < transactions.length; i += 5) {
    const slice = transactions.slice(i, i + 5);
    const amount = slice.reduce((sum, item) => sum + item.net, 0);
    const created = slice[0]?.created_at || new Date().toISOString();
    groups.push({
      id: `pay_${String(i / 5 + 1).padStart(4, "0")}`,
      practitioner_id: practitionerId,
      amount,
      currency: "USD",
      payout_status: randomStatus(i),
      payout_provider: "stripe",
      payout_method: "bank_account",
      payout_date: created,
      processing_date: created,
      created_at: created,
      transaction_count: slice.length,
      notes: null
    });
  }
  return groups;
}

function aggregateTrend(values: number[]): number[] {
  const buckets = Array.from({ length: 8 }, () => 0);
  values.forEach((value, index) => {
    buckets[index % buckets.length] += value;
  });
  return buckets.map((value) => Number(value.toFixed(2)));
}
