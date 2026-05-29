<template>
  <section class="stack">
    <article class="card top">
      <p class="eyebrow">Payouts</p>
      <h1>Balance</h1>
      <p class="sub">Track what is available now and what is pending.</p>
    </article>

    <section class="balance-grid">
      <article class="card metric">
        <p>Available</p>
        <strong>{{ formatMoney(availableBalance) }}</strong>
      </article>
      <article class="card metric">
        <p>Pending</p>
        <strong>{{ formatMoney(pendingPayouts) }}</strong>
      </article>
    </section>

    <article class="card">
      <button class="btn primary" type="button" @click="withdraw">Withdraw</button>
      <p class="sub">Withdrawals are processed through your connected payout method.</p>
    </article>

    <article class="card">
      <div class="row">
        <p class="eyebrow">Recent payouts</p>
        <button class="btn" type="button" :disabled="loading" @click="load">Refresh</button>
      </div>
      <p v-if="loading" class="sub">Loading payouts…</p>
      <p v-else-if="error" class="sub error">{{ error }}</p>
      <div v-else-if="payouts.length" class="list">
        <article v-for="payout in payouts.slice(0, 6)" :key="payout.id" class="item">
          <div>
            <p class="id">{{ payout.id }}</p>
            <p class="meta">{{ new Date(payout.created_at).toLocaleDateString() }}</p>
          </div>
          <strong>{{ formatMoney(payout.amount) }}</strong>
        </article>
      </div>
      <p v-else class="sub">No payouts yet.</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";
import { usePayoutDashboard } from "../composables/usePayoutDashboard";
import { showToast } from "../stores/toast";

const { availableBalance, pendingPayouts, payouts, loading, error, load, formatMoney } = usePayoutDashboard();

function withdraw() {
  showToast("Withdrawal flow is available in Advanced Workspace.", "warning");
}

onMounted(load);
</script>

<style scoped>
.stack { display: grid; gap: 14px; padding-bottom: 80px; }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: 16px; background: rgba(10,20,36,.72); padding: 16px; display: grid; gap: 10px; }
.top { background: linear-gradient(170deg, rgba(17,37,66,.9), rgba(9,17,30,.86)); }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
h1 { margin: 0; font-size: 28px; line-height: 1.06; }
.sub { margin: 0; color: rgba(230,238,249,.74); }
.sub.error { color: #ffb2b2; }
.balance-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.metric p { margin: 0; font-size: 12px; color: rgba(230,238,249,.68); text-transform: uppercase; letter-spacing: .08em; }
.metric strong { font-size: 30px; letter-spacing: -.02em; }
.btn { min-height: 44px; border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; width: fit-content; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; width: 100%; }
.row { display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.list { display: grid; gap: 8px; }
.item { border: 1px solid rgba(255,255,255,.1); border-radius: 10px; background: rgba(255,255,255,.03); padding: 10px; display: flex; justify-content: space-between; gap: 8px; align-items: center; }
.id, .meta { margin: 0; }
.meta { font-size: 12px; color: rgba(230,238,249,.66); }
@media (max-width: 640px) { .balance-grid { grid-template-columns: 1fr; } }
</style>
