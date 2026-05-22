<template>
  <section class="wallet-passes">
    <header class="wallet-passes__head">
      <div>
        <p class="eyebrow">Wallet Passes</p>
        <h1>Pass Center</h1>
        <p>Track active, redeemed, and expiring passes with quick actions.</p>
      </div>
      <div class="head-actions">
        <AppButton variant="secondary" size="form" :disabled="loading" @click="load">Refresh</AppButton>
      </div>
    </header>

    <AppCard v-if="loading" muted>Loading wallet passes…</AppCard>
    <AppCard v-else-if="errorText" class="error-card">{{ errorText }}</AppCard>

    <template v-else>
      <div class="chips">
        <button class="chip" :class="{ 'is-active': tab === 'active' }" @click="tab = 'active'">Active ({{ activePasses.length }})</button>
        <button class="chip" :class="{ 'is-active': tab === 'redeemed' }" @click="tab = 'redeemed'">Redeemed ({{ redeemedPasses.length }})</button>
        <button class="chip" :class="{ 'is-active': tab === 'expiring' }" @click="tab = 'expiring'">Expiring ({{ expiringPasses.length }})</button>
      </div>

      <div v-if="visiblePasses.length === 0" class="empty-state">
        <h2>No passes yet</h2>
        <p>Once customers complete checkout, wallet passes will appear here.</p>
      </div>

      <div v-else class="pass-grid">
        <article v-for="pass in visiblePasses" :key="pass.id" class="pass-card">
          <div class="pass-top">
            <p class="pass-id">#{{ pass.id.slice(0, 8) }}</p>
            <span class="status" :class="statusTone(pass.status)">{{ pass.status }}</span>
          </div>

          <h3>{{ pass.wallet_type.toUpperCase() }} Pass</h3>
          <p class="meta">Created {{ formatDate(pass.created_at) }}</p>
          <p class="meta">Deal ID {{ pass.deal_id.slice(0, 8) }}</p>

          <div class="qr">▦</div>
          <p class="hint">{{ pass.status === 'redeemed' ? 'Redeemed successfully' : 'Hold near reader / scan QR' }}</p>

          <div class="actions">
            <AppButton v-if="pass.status !== 'redeemed'" variant="secondary" @click="onRedeem(pass.qr_code)">Redeem</AppButton>
            <AppButton v-if="pass.status === 'redeemed'" variant="ghost" @click="onRestore(pass.id)">Restore</AppButton>
          </div>
        </article>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import { listWalletPasses, redeemWalletPass, restoreWalletPass, type WalletPassPayload } from "../services/api";
import { sessionState } from "../stores/session";

type Tab = "active" | "redeemed" | "expiring";

const tab = ref<Tab>("active");
const loading = ref(true);
const errorText = ref("");
const passes = ref<WalletPassPayload[]>([]);

const activePasses = computed(() => passes.value.filter((p) => p.status === "active" || p.status === "inactive"));
const redeemedPasses = computed(() => passes.value.filter((p) => p.status === "redeemed"));
const expiringPasses = computed(() => passes.value.filter((p) => p.status === "expired"));

const visiblePasses = computed(() => {
  if (tab.value === "redeemed") return redeemedPasses.value;
  if (tab.value === "expiring") return expiringPasses.value;
  return activePasses.value;
});

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function statusTone(status: string) {
  if (status === "redeemed") return "is-green";
  if (status === "expired") return "is-red";
  return "is-amber";
}

async function load() {
  loading.value = true;
  errorText.value = "";
  if (!sessionState.token) {
    loading.value = false;
    errorText.value = "Authentication session expired.";
    return;
  }
  try {
    passes.value = await listWalletPasses(sessionState.token);
  } catch (err) {
    errorText.value = `Failed to load wallet passes: ${String(err)}`;
  } finally {
    loading.value = false;
  }
}

async function onRedeem(qrCode: string) {
  if (!sessionState.token) return;
  try {
    await redeemWalletPass(sessionState.token, qrCode);
    await load();
  } catch (err) {
    errorText.value = `Redeem failed: ${String(err)}`;
  }
}

async function onRestore(passId: string) {
  if (!sessionState.token) return;
  try {
    await restoreWalletPass(sessionState.token, passId);
    await load();
  } catch (err) {
    errorText.value = `Restore failed: ${String(err)}`;
  }
}

onMounted(load);
</script>

<style scoped>
.wallet-passes { padding: 18px; display: grid; gap: 12px; }
.wallet-passes__head { display: flex; justify-content: space-between; gap: 12px; align-items: flex-start; }
.wallet-passes__head h1 { margin: 6px 0 0; font-size: clamp(30px, 4vw, 46px); }
.wallet-passes__head p { margin: 8px 0 0; color: rgba(255,255,255,.66); }
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { border-radius: 999px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.03); color: rgba(255,255,255,.75); padding: 8px 12px; font-size: 12px; }
.chip.is-active { border-color: rgba(240,190,100,.5); background: rgba(240,190,100,.15); color: #f4d8a7; }
.error-card { border: 1px solid rgba(255,100,100,.55); color: #ffd0d0; }
.empty-state { border-radius: 16px; border: 1px dashed rgba(255,255,255,.22); padding: 20px; text-align: center; }
.empty-state h2 { margin: 0; }
.empty-state p { margin: 8px 0 0; color: rgba(255,255,255,.62); }
.pass-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; }
.pass-card { border-radius: 18px; border: 1px solid rgba(255,255,255,.1); background: linear-gradient(180deg, rgba(14,22,35,.78), rgba(10,16,30,.72)); padding: 14px; transition: transform 180ms ease, box-shadow 180ms ease; }
.pass-card:hover { transform: translateY(-2px); box-shadow: 0 14px 38px rgba(0,0,0,.28); }
.pass-top { display: flex; justify-content: space-between; align-items: center; }
.pass-id { margin: 0; color: rgba(255,255,255,.58); font-size: 12px; }
.status { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.status.is-green { color: #52d58b; }
.status.is-red { color: #f08a6b; }
.status.is-amber { color: #f4d8a7; }
.pass-card h3 { margin: 10px 0 0; font-size: 21px; }
.meta { margin: 6px 0 0; color: rgba(255,255,255,.64); font-size: 13px; }
.qr { margin-top: 12px; height: 88px; border-radius: 12px; background: rgba(255,255,255,.95); color: #111; display: grid; place-items: center; font-size: 30px; }
.hint { margin: 8px 0 0; color: rgba(255,255,255,.6); font-size: 12px; }
.actions { margin-top: 10px; display: flex; gap: 8px; }
@media (max-width: 1180px) { .pass-grid { grid-template-columns: repeat(2, minmax(0,1fr)); } }
@media (max-width: 767px) {
  .wallet-passes { padding: 12px; }
  .wallet-passes__head { flex-direction: column; }
  .pass-grid { grid-template-columns: 1fr; }
}
</style>
