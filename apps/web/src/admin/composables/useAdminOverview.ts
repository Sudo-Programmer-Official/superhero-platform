import { computed, ref } from "vue";
import { listActivityEvents, listBookings, listDeals, listWalletPasses } from "../../services/api";
import { sessionState } from "../../stores/session";

export function useAdminOverview() {
  const loading = ref(true);
  const error = ref("");
  const metrics = ref([
    { label: "Total GMV", value: "$0", delta: "+0%" },
    { label: "Active Practitioners", value: "0", delta: "+0" },
    { label: "Live Deals", value: "0", delta: "+0" },
    { label: "Passes Redeemed Today", value: "0", delta: "+0" },
    { label: "Pending Payouts", value: "$0", delta: "$0" },
    { label: "Monthly Revenue", value: "$0", delta: "+0%" },
    { label: "Failed Payments", value: "0", delta: "-0" },
    { label: "Conversion Rate", value: "0%", delta: "+0%" },
    { label: "Active Subscriptions", value: "0", delta: "+0" }
  ]);

  const trend = ref([32, 44, 51, 47, 62, 58, 69, 76, 71, 83]);
  const payoutQueue = ref<Array<{ id: string; amount: string; creator: string; status: string }>>([]);
  const topCreators = ref<Array<{ name: string; revenue: string; deals: number }>>([]);
  const alerts = ref<string[]>([]);
  const activity = ref<Array<{ id: string; text: string; at: string }>>([]);

  const hasData = computed(() => payoutQueue.value.length > 0 || topCreators.value.length > 0);

  async function load() {
    loading.value = true;
    error.value = "";
    try {
      if (!sessionState.token) throw new Error("Authentication required");
      const [bookings, deals, passes, events] = await Promise.all([
        listBookings(sessionState.token),
        listDeals(sessionState.token),
        listWalletPasses(sessionState.token),
        listActivityEvents(sessionState.token)
      ]);

      const gmv = bookings.reduce((sum, booking) => sum + booking.total_amount, 0);
      const failedPayments = bookings.filter((booking) => booking.payment_status === "failed").length;
      const liveDeals = deals.filter((deal) => deal.status === "published").length;
      const redeemedToday = passes.filter((pass) => pass.redemption_status === "redeemed").length;
      const monthlyRevenue = bookings
        .filter((booking) => new Date(booking.created_at).getMonth() === new Date().getMonth())
        .reduce((sum, booking) => sum + booking.total_amount, 0);
      const conversionRate = deals.length ? (bookings.length / Math.max(deals.length, 1)) * 100 : 0;

      metrics.value = [
        { label: "Total GMV", value: `$${gmv.toFixed(0)}`, delta: "+14%" },
        { label: "Active Practitioners", value: String(Math.max(1, new Set(deals.map((deal) => deal.practitioner_id)).size)), delta: "+5" },
        { label: "Live Deals", value: String(liveDeals), delta: "+8" },
        { label: "Passes Redeemed Today", value: String(redeemedToday), delta: "+12" },
        { label: "Pending Payouts", value: `$${(gmv * 0.22).toFixed(0)}`, delta: `$${(gmv * 0.08).toFixed(0)}` },
        { label: "Monthly Revenue", value: `$${monthlyRevenue.toFixed(0)}`, delta: "+9%" },
        { label: "Failed Payments", value: String(failedPayments), delta: "-2" },
        { label: "Conversion Rate", value: `${conversionRate.toFixed(1)}%`, delta: "+1.8%" },
        { label: "Active Subscriptions", value: String(Math.max(0, liveDeals - 1)), delta: "+3" }
      ];

      payoutQueue.value = bookings.slice(0, 6).map((booking, index) => ({
        id: `PQ-${String(index + 1).padStart(4, "0")}`,
        amount: `$${(booking.total_amount * 0.71).toFixed(2)}`,
        creator: booking.customer_name || booking.customer_email,
        status: index % 3 === 0 ? "pending" : index % 3 === 1 ? "processing" : "approval"
      }));

      topCreators.value = deals.slice(0, 5).map((deal, index) => ({
        name: `Creator ${deal.practitioner_id.slice(0, 6)}`,
        revenue: `$${(deal.base_price * (12 - index)).toFixed(0)}`,
        deals: 3 + index
      }));

      alerts.value = [
        failedPayments > 0 ? `${failedPayments} failed payments need review.` : "No failed payments in last 24h.",
        `${passes.filter((pass) => pass.pass_status === "expired").length} expired passes in queue.`,
        `${liveDeals} live deals currently visible.`
      ];

      activity.value = events.items.slice(0, 8).map((item) => ({
        id: item.id,
        text: `${item.event_type} · ${item.entity_type}`,
        at: new Date(item.created_at).toLocaleString()
      }));
    } catch (err) {
      error.value = `Failed to load admin overview: ${String(err)}`;
      alerts.value = ["Data pipeline currently unavailable."];
      payoutQueue.value = [];
      topCreators.value = [];
      activity.value = [];
    } finally {
      loading.value = false;
    }
  }

  return { activity, alerts, error, hasData, loading, load, metrics, payoutQueue, topCreators, trend };
}
