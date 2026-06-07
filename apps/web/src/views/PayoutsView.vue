<template>
  <section class="stack">
    <article class="card hero">
      <div class="hero-copy">
        <p class="eyebrow">Payouts</p>
        <h1>Balance</h1>
        <p class="sub">See how much money is available now and which deals made it.</p>
      </div>

      <div class="hero-balance">
        <p class="label">Available now</p>
        <strong>{{ formatMoney(availableBalance) }}</strong>
        <p class="sub hero-note">
          {{ stripeBadge.label }}
          <span v-if="nextPayoutDate"> · Next payout {{ new Date(nextPayoutDate).toLocaleDateString() }}</span>
        </p>
        <div class="hero-actions">
          <button class="btn primary" type="button" @click="primaryAction()">{{ primaryActionLabel }}</button>
          <button class="btn" type="button" :disabled="loading" @click="load">Refresh</button>
        </div>
      </div>
    </article>

    <article class="card">
      <div class="section-head">
        <div>
          <p class="eyebrow">Revenue by deal</p>
          <h2>Chronological view</h2>
        </div>
        <span class="badge" :class="`is-${stripeBadge.tone}`">{{ stripeBadge.label }}</span>
      </div>

      <p v-if="loading" class="sub">Loading revenue by deal…</p>
      <p v-else-if="error" class="sub error">{{ error }}</p>
      <p v-else-if="revenueByDeal.length === 0" class="sub">No deal revenue found yet.</p>

      <div v-else class="deal-grid">
        <article v-for="deal in revenueByDeal" :key="deal.id" class="deal-card" :class="{ 'is-open': expandedDealId === deal.id }">
          <button class="deal-toggle" type="button" @click="toggleDeal(deal.id)">
            <div class="cover-wrap">
              <img v-if="deal.cover" :src="deal.cover" alt="Deal cover" class="cover" />
              <div v-else class="cover cover--fallback"></div>
            </div>
            <div class="deal-copy">
              <p class="eyebrow">Deal revenue</p>
              <h3>{{ deal.title }}</h3>
              <p class="meta">{{ formatMoney(deal.revenue) }} generated · {{ deal.claimed }} claimed · {{ deal.redeemed }} redeemed</p>
              <div class="deal-metrics" aria-label="Deal revenue summary">
                <span class="deal-metric"><strong>{{ formatMoney(deal.revenue) }}</strong><small>Revenue</small></span>
                <span class="deal-metric"><strong>{{ deal.claimed }}</strong><small>Claimed</small></span>
                <span class="deal-metric"><strong>{{ deal.redeemed }}</strong><small>Redeemed</small></span>
              </div>
              <p class="meta">Last activity {{ formatDate(deal.latest_activity_at) }}</p>
            </div>
            <span class="toggle-label">{{ expandedDealId === deal.id ? "Hide" : "View" }}</span>
          </button>

          <transition name="fade-slide">
            <div v-if="expandedDealId === deal.id" class="deal-details">
              <div class="detail-grid">
                <article class="detail-card">
                  <p class="detail-label">Revenue details</p>
                  <strong>{{ formatMoney(deal.revenue) }}</strong>
                  <p class="detail-meta">Gross {{ formatMoney(deal.gross) }}</p>
                  <p class="detail-meta">Fees {{ formatMoney(deal.fees) }}</p>
                  <p class="detail-meta">Net {{ formatMoney(deal.net) }}</p>
                </article>

                <article class="detail-card">
                  <p class="detail-label">Customers</p>
                  <div v-if="deal.customers.length" class="customer-list">
                    <div v-for="customer in deal.customers" :key="`${deal.id}-${customer.id}`" class="customer-row">
                      <div>
                        <p class="customer-name">{{ customer.name }}</p>
                        <p class="meta">{{ customer.email }}</p>
                      </div>
                      <div class="customer-chip-group">
                        <span class="chip">{{ formatMoney(customer.amount) }}</span>
                        <span class="chip">{{ customer.status }}</span>
                      </div>
                    </div>
                  </div>
                  <p v-else class="meta">No customer records yet.</p>
                </article>

                <article class="detail-card">
                  <p class="detail-label">Transactions</p>
                  <div v-if="deal.transactions.length" class="transaction-list">
                    <div v-for="transaction in deal.transactions" :key="transaction.id" class="transaction-row">
                      <div>
                        <p class="transaction-title">{{ transaction.booking_number }}</p>
                        <p class="meta">{{ transaction.customer }}</p>
                      </div>
                      <div class="transaction-meta">
                        <span class="chip">{{ formatMoney(transaction.amount) }}</span>
                        <span class="chip">{{ transaction.payment_status }}</span>
                        <span class="chip">{{ transaction.redemption_status }}</span>
                      </div>
                    </div>
                  </div>
                  <p v-else class="meta">No transaction history yet.</p>
                </article>
              </div>
            </div>
          </transition>
        </article>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { usePayoutDashboard } from "../composables/usePayoutDashboard";

const router = useRouter();
const expandedDealId = ref<string | null>(null);

const {
  availableBalance,
  error,
  load,
  loading,
  nextPayoutDate,
  primaryActionLabel,
  revenueByDeal,
  stripeBadge,
  stripeState,
  formatMoney
} = usePayoutDashboard();

function primaryAction() {
  if (!stripeState.value.stripe_account_id) {
    void router.push({ name: "settings" });
    return;
  }
  void router.push({ name: "payouts" });
}

function toggleDeal(dealId: string) {
  expandedDealId.value = expandedDealId.value === dealId ? null : dealId;
}

function formatDate(value: string) {
  return new Date(value).toLocaleDateString();
}

onMounted(load);
</script>

<style scoped>
.stack {
  display: grid;
  gap: 14px;
  padding-bottom: calc(108px + env(safe-area-inset-bottom, 0px));
}

.card {
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 18px;
  background: rgba(10, 20, 36, .72);
  padding: 16px;
  display: grid;
  gap: 12px;
}

.hero {
  background: linear-gradient(170deg, rgba(17, 37, 66, .92), rgba(9, 17, 30, .88));
}

.hero-copy {
  display: grid;
  gap: 8px;
}

.hero-balance {
  display: grid;
  gap: 10px;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, .08);
  background: rgba(255, 255, 255, .03);
  padding: 16px;
}

.eyebrow {
  margin: 0;
  font-size: 11px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: #f4d8a7;
}

h1, h2, h3 {
  margin: 0;
  letter-spacing: -0.02em;
}

h1 {
  font-size: 30px;
  line-height: 1.05;
}

h2 {
  font-size: 24px;
}

h3 {
  font-size: 20px;
  line-height: 1.1;
}

.label {
  margin: 0;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .08em;
  color: rgba(230, 238, 249, .7);
}

.hero-balance strong {
  font-size: 44px;
  line-height: 1;
}

.sub {
  margin: 0;
  color: rgba(230, 238, 249, .74);
  font-size: 14px;
}

.sub.error {
  color: #ffb2b2;
}

.hero-note {
  font-size: 13px;
}

.hero-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn {
  min-height: 44px;
  border-radius: 10px;
  border: 1px solid rgba(255, 255, 255, .14);
  background: rgba(255, 255, 255, .05);
  color: #e8eef8;
  padding: 0 12px;
}

.btn.primary {
  border-color: rgba(240, 190, 100, .46);
  color: #0c1728;
  background: linear-gradient(145deg, #f3d89f, #e9c57b);
  font-weight: 700;
}

.btn:disabled {
  opacity: .55;
  cursor: not-allowed;
}

.section-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.badge {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, .14);
  padding: 6px 10px;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .08em;
}

.badge.is-green {
  color: #52d58b;
  border-color: rgba(82, 213, 139, .35);
}

.badge.is-amber {
  color: #f4d8a7;
  border-color: rgba(240, 190, 100, .35);
}

.badge.is-red {
  color: #ffb5b5;
  border-color: rgba(255, 120, 120, .35);
}

.badge.is-cyan {
  color: #8fd0ff;
  border-color: rgba(143, 208, 255, .35);
}

.deal-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.deal-card {
  border: 1px solid rgba(255, 255, 255, .12);
  border-radius: 16px;
  background: rgba(8, 14, 24, .7);
  overflow: hidden;
}

.deal-toggle {
  width: 100%;
  border: 0;
  background: transparent;
  color: inherit;
  text-align: left;
  padding: 0;
  display: grid;
  gap: 0;
}

.cover-wrap {
  overflow: hidden;
  aspect-ratio: 1.18 / 1;
}

.cover {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.cover--fallback {
  background: linear-gradient(135deg, rgba(30, 49, 78, .88), rgba(8, 14, 25, .95));
}

.deal-copy {
  display: grid;
  gap: 6px;
  padding: 14px 14px 12px;
}

.deal-metrics {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 8px;
  margin-top: 6px;
}

.deal-metric {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, .08);
  background: rgba(255, 255, 255, .03);
  padding: 8px 10px;
  display: grid;
  gap: 2px;
}

.deal-metric strong {
  font-size: 15px;
  line-height: 1;
}

.deal-metric small {
  color: rgba(230, 238, 249, .62);
  font-size: 10px;
  text-transform: uppercase;
  letter-spacing: .08em;
}

.meta {
  margin: 0;
  color: rgba(230, 238, 249, .72);
  font-size: 13px;
}

.toggle-label {
  margin: 0 14px 14px;
  justify-self: start;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, .12);
  padding: 6px 10px;
  font-size: 12px;
  color: rgba(230, 238, 249, .84);
  background: rgba(255, 255, 255, .04);
}

.deal-details {
  border-top: 1px solid rgba(255, 255, 255, .08);
  padding: 14px;
}

.detail-grid {
  display: grid;
  gap: 10px;
}

.detail-card {
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, .1);
  background: rgba(255, 255, 255, .03);
  padding: 12px;
  display: grid;
  gap: 6px;
}

.detail-label {
  margin: 0;
  font-size: 11px;
  letter-spacing: .12em;
  text-transform: uppercase;
  color: rgba(244, 216, 167, .9);
}

.detail-meta {
  margin: 0;
  color: rgba(230, 238, 249, .72);
  font-size: 13px;
}

.customer-list,
.transaction-list {
  display: grid;
  gap: 8px;
}

.customer-row,
.transaction-row {
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, .08);
  background: rgba(255, 255, 255, .02);
  padding: 10px;
  display: grid;
  gap: 8px;
}

.customer-name,
.transaction-title {
  margin: 0;
  font-weight: 700;
}

.customer-chip-group,
.transaction-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.chip {
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, .16);
  padding: 4px 8px;
  font-size: 11px;
  color: rgba(230, 238, 249, .84);
  background: rgba(255, 255, 255, .04);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 180ms ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

@media (max-width: 1100px) {
  .deal-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 720px) {
  .deal-grid {
    grid-template-columns: 1fr;
  }

  .section-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .hero-balance strong {
    font-size: 40px;
  }

  .deal-metrics {
    grid-template-columns: 1fr;
  }
}
</style>
