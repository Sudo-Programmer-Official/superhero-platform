<template>
  <DashboardPageShell
    eyebrow="Payouts"
    title="Creator Earnings Hub"
    subtitle="Track revenue, pending balances, payout timing, and settlement operations in one trusted financial center."
  >
    <template #actions>
      <AppButton variant="secondary" size="form" :disabled="loading" @click="load">Refresh</AppButton>
    </template>

    <PaddedSectionCard v-if="loading" muted>Loading payouts dashboard…</PaddedSectionCard>
    <PaddedSectionCard v-else-if="error" class="error-card">{{ error }}</PaddedSectionCard>

    <template v-else>
      <section class="metrics-grid">
        <article class="metric-card">
          <p>Total Revenue</p>
          <strong>{{ formatMoney(totalRevenue) }}</strong>
        </article>
        <article class="metric-card">
          <p>Available Balance</p>
          <strong>{{ formatMoney(availableBalance) }}</strong>
        </article>
        <article class="metric-card">
          <p>Pending Payouts</p>
          <strong>{{ formatMoney(pendingPayouts) }}</strong>
        </article>
        <article class="metric-card">
          <p>Next Payout</p>
          <strong>{{ nextPayoutDate ? new Date(nextPayoutDate).toLocaleDateString() : "Not scheduled" }}</strong>
        </article>
      </section>

      <section class="upper-grid">
        <PaddedSectionCard>
          <div class="section-head">
            <h3>Stripe Connection</h3>
            <span class="badge" :class="`is-${stripeBadge.tone}`">{{ stripeBadge.label }}</span>
          </div>
          <p class="helper">Connect Stripe to unlock live payouts, reconciliation, and transfer tracking.</p>
          <div class="status-grid">
            <p><span>Account ID</span><strong>{{ stripeState.stripe_account_id || "Not connected" }}</strong></p>
            <p><span>Onboarding</span><strong>{{ stripeState.onboarding_state }}</strong></p>
            <p><span>Payouts Enabled</span><strong>{{ stripeState.payouts_enabled ? "Yes" : "No" }}</strong></p>
            <p><span>Charges Enabled</span><strong>{{ stripeState.charges_enabled ? "Yes" : "No" }}</strong></p>
          </div>
          <AppButton variant="primary">{{ stripeBadge.cta }}</AppButton>
        </PaddedSectionCard>

        <PaddedSectionCard>
          <h3>Payout Timeline</h3>
          <div class="timeline">
            <article v-for="payout in payouts.slice(0, 6)" :key="payout.id" class="timeline-item">
              <div>
                <p class="timeline-id">{{ payout.id }}</p>
                <p class="timeline-meta">{{ new Date(payout.created_at).toLocaleDateString() }} · {{ payout.transaction_count }} txns</p>
              </div>
              <div class="timeline-right">
                <span class="badge" :class="`is-${payoutStatusTone(payout.payout_status)}`">{{ payoutStatusLabel(payout.payout_status) }}</span>
                <strong>{{ formatMoney(payout.amount) }}</strong>
              </div>
            </article>
          </div>
        </PaddedSectionCard>
      </section>

      <section class="charts-grid">
        <PaddedSectionCard>
          <h3>Revenue Trend</h3>
          <div class="sparkline">
            <span v-for="(point, idx) in revenueTrend" :key="`rev-${idx}`" :style="barStyle(point, revenueTrend)"></span>
          </div>
        </PaddedSectionCard>
        <PaddedSectionCard>
          <h3>Bookings Trend</h3>
          <div class="sparkline">
            <span v-for="(point, idx) in bookingsTrend" :key="`book-${idx}`" :style="barStyle(point, bookingsTrend)"></span>
          </div>
        </PaddedSectionCard>
        <PaddedSectionCard>
          <h3>Payout Trend</h3>
          <div class="sparkline">
            <span v-for="(point, idx) in payoutTrend" :key="`pay-${idx}`" :style="barStyle(point, payoutTrend)"></span>
          </div>
        </PaddedSectionCard>
      </section>

      <PaddedSectionCard>
        <h3>Financial Breakdown</h3>
        <div class="breakdown-grid">
          <p><span>Gross Revenue</span><strong>{{ formatMoney(grossRevenue) }}</strong></p>
          <p><span>Platform Fees</span><strong>{{ formatMoney(platformFees) }}</strong></p>
          <p><span>Stripe Fees</span><strong>{{ formatMoney(stripeFees) }}</strong></p>
          <p><span>Refunds</span><strong>{{ formatMoney(refunded) }}</strong></p>
          <p><span>Net Revenue</span><strong>{{ formatMoney(netRevenue) }}</strong></p>
        </div>
      </PaddedSectionCard>

      <PaddedSectionCard>
        <div class="section-head">
          <h3>Transactions</h3>
          <AppButton variant="ghost" @click="exportCsv">Export CSV</AppButton>
        </div>
        <div class="controls">
          <input v-model="query" class="input" placeholder="Search customer, deal, or payout batch" />
          <select v-model="statusFilter" class="input input--select">
            <option value="all">All statuses</option>
            <option value="pending">Pending</option>
            <option value="processing">Processing</option>
            <option value="paid">Paid</option>
            <option value="failed">Failed</option>
            <option value="refunded">Refunded</option>
          </select>
        </div>

        <div v-if="filteredTransactions.length === 0" class="empty-state">
          <h4>No transactions yet</h4>
          <p>Create your first deal to start earning revenue.</p>
        </div>

        <div v-else class="table-wrap">
          <table class="tx-table">
            <thead>
              <tr>
                <th>Customer</th>
                <th>Deal</th>
                <th>Gross</th>
                <th>Fees</th>
                <th>Net</th>
                <th>Status</th>
                <th>Payout Batch</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="item in visibleTransactions" :key="item.id">
                <td>{{ item.customer }}</td>
                <td>{{ item.deal }}</td>
                <td>{{ formatMoney(item.gross) }}</td>
                <td>{{ formatMoney(item.platform_fees + item.stripe_fees) }}</td>
                <td>{{ formatMoney(item.net) }}</td>
                <td><span class="badge" :class="`is-${payoutStatusTone(item.status)}`">{{ payoutStatusLabel(item.status) }}</span></td>
                <td>{{ item.payout_batch }}</td>
                <td>{{ new Date(item.created_at).toLocaleDateString() }}</td>
              </tr>
            </tbody>
          </table>
          <div class="pager">
            <AppButton variant="ghost" :disabled="page <= 1" @click="goPrevPage">Previous</AppButton>
            <p>Page {{ page }} / {{ totalPages }}</p>
            <AppButton variant="ghost" :disabled="page >= totalPages" @click="goNextPage">Next</AppButton>
          </div>
        </div>
      </PaddedSectionCard>
    </template>
  </DashboardPageShell>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { payoutStatusLabel, payoutStatusTone } from "../domain/payout";
import { usePayoutDashboard } from "../composables/usePayoutDashboard";
import DashboardPageShell from "../design-system/patterns/DashboardPageShell.vue";
import PaddedSectionCard from "../design-system/patterns/PaddedSectionCard.vue";
import AppButton from "../design-system/primitives/AppButton.vue";

const {
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
  visibleTransactions
} = usePayoutDashboard();

function barStyle(value: number, values: number[]) {
  const max = Math.max(...values, 1);
  const height = Math.max(10, Math.round((value / max) * 100));
  return { height: `${height}%` };
}

onMounted(load);
</script>

<style scoped>
.error-card { border: 1px solid rgba(255,100,100,.5); color: #ffd0d0; }
.metrics-grid { display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 20px; }
.metric-card { border-radius: 20px; border: 1px solid rgba(193,218,255,.14); background: linear-gradient(180deg, rgba(18,30,52,.76), rgba(10,16,28,.86)); padding: 18px; box-shadow: 0 14px 34px rgba(0,0,0,.24), 0 1px 0 rgba(255,255,255,.08) inset; }
.metric-card p { margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.62); }
.metric-card strong { display: block; margin-top: 12px; font-size: 34px; letter-spacing: -0.02em; }
.upper-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }
.section-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.section-head h3 { margin: 0; font-size: 24px; }
.helper { margin: 8px 0 0; color: rgba(255,255,255,.66); }
.status-grid { margin: 16px 0; display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.status-grid p, .breakdown-grid p { margin: 0; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 12px; display: grid; gap: 6px; }
.status-grid span, .breakdown-grid span { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.58); }
.status-grid strong, .breakdown-grid strong { font-size: 17px; }
.badge { border-radius: 999px; border: 1px solid rgba(255,255,255,.16); padding: 5px 9px; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.badge.is-green { color: #52d58b; border-color: rgba(82,213,139,.45); }
.badge.is-amber { color: #f4d8a7; border-color: rgba(240,190,100,.45); }
.badge.is-red { color: #ffb5b5; border-color: rgba(255,120,120,.45); }
.badge.is-cyan { color: #9fd0ff; border-color: rgba(113,182,255,.5); }
.timeline { display: grid; gap: 12px; }
.timeline-item { border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 12px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.timeline-id { margin: 0; font-size: 13px; color: rgba(255,255,255,.9); }
.timeline-meta { margin: 4px 0 0; font-size: 12px; color: rgba(255,255,255,.56); }
.timeline-right { display: grid; justify-items: end; gap: 8px; }
.timeline-right strong { font-size: 16px; }
.charts-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 20px; }
.sparkline { height: 120px; display: grid; grid-auto-flow: column; gap: 8px; align-items: end; }
.sparkline span { border-radius: 10px 10px 4px 4px; background: linear-gradient(180deg, rgba(113,182,255,.86), rgba(36,68,120,.88)); box-shadow: 0 8px 20px rgba(30,66,128,.28); }
.breakdown-grid { display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 12px; }
.controls { margin-top: 12px; display: grid; grid-template-columns: 1fr 220px; gap: 12px; }
.input { min-height: 46px; border-radius: 12px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,18,30,.62); color: #dbe5f3; padding: 0 12px; }
.input--select { padding-right: 28px; }
.empty-state { margin-top: 14px; border-radius: 14px; border: 1px dashed rgba(255,255,255,.2); padding: 20px; text-align: center; }
.empty-state h4 { margin: 0; font-size: 24px; }
.empty-state p { margin: 8px 0 0; color: rgba(255,255,255,.64); }
.table-wrap { margin-top: 14px; overflow: auto; }
.tx-table { width: 100%; min-width: 980px; border-collapse: collapse; }
.tx-table th { text-align: left; padding: 12px; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.58); border-bottom: 1px solid rgba(255,255,255,.12); }
.tx-table td { padding: 12px; border-bottom: 1px solid rgba(255,255,255,.08); }
.pager { margin-top: 12px; display: flex; justify-content: space-between; align-items: center; }
.pager p { margin: 0; color: rgba(255,255,255,.7); }
@media (max-width: 1279px) {
  .metrics-grid { grid-template-columns: repeat(2, minmax(0,1fr)); }
  .upper-grid, .charts-grid { grid-template-columns: 1fr; }
  .breakdown-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 767px) {
  .metrics-grid, .status-grid, .controls, .breakdown-grid { grid-template-columns: 1fr; }
}
</style>
