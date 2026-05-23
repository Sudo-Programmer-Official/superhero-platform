<template>
  <DashboardPageShell
    eyebrow="Wallet Passes"
    title="Pass Center"
    subtitle="Track active, redeemed, and expiring passes with quick actions."
  >
    <template #actions>
      <AppButton variant="secondary" size="form" :disabled="loading" @click="load">Refresh</AppButton>
    </template>

    <PaddedSectionCard v-if="loading">
      <AppLoadingState title="Loading wallet passes" description="Syncing pass lifecycle and redemption states." />
    </PaddedSectionCard>
    <PaddedSectionCard v-else-if="errorText">
      <AppErrorState title="Wallet pass sync failed" :description="errorText" />
    </PaddedSectionCard>

    <template v-else>
      <PaddedSectionCard v-if="checkoutSyncActive" class="sync-card">
        <strong>Checkout detected</strong>
        <p>We are syncing newly issued passes. This view auto-refreshes for a short window.</p>
      </PaddedSectionCard>

      <div class="chips">
        <button class="chip" :class="{ 'is-active': tab === 'active' }" @click="tab = 'active'">Active ({{ activePasses.length }})</button>
        <button class="chip" :class="{ 'is-active': tab === 'redeemed' }" @click="tab = 'redeemed'">Redeemed ({{ redeemedPasses.length }})</button>
        <button class="chip" :class="{ 'is-active': tab === 'expiring' }" @click="tab = 'expiring'">Expiring ({{ expiringPasses.length }})</button>
      </div>

      <PaddedSectionCard v-if="visiblePasses.length === 0" class="empty-state" muted>
        <h2>No passes yet</h2>
        <p>Once customers complete checkout, wallet passes will appear here.</p>
      </PaddedSectionCard>

      <div v-else class="pass-grid">
        <article v-for="pass in visiblePasses" :key="pass.id" class="pass-card">
          <div class="pass-top">
            <p class="pass-id">#{{ pass.id.slice(0, 8) }}</p>
            <span class="status" :class="`is-${statusTone(pass)}`">
              {{ statusIcon(pass) }} {{ statusLabel(pass) }}
            </span>
          </div>

          <h3>{{ (pass.wallet_provider || pass.wallet_type).toUpperCase() }} Pass</h3>
          <p class="meta">Created {{ formatDate(pass.created_at) }}</p>
          <p v-if="pass.expires_at" class="meta">Expires {{ formatDate(pass.expires_at) }}</p>
          <p class="meta">Deal ID {{ pass.deal_id.slice(0, 8) }}</p>
          <p v-if="pass.booking_id" class="meta">Booking ID {{ pass.booking_id.slice(0, 8) }}</p>

          <div class="qr">▦</div>
          <p class="hint">{{ statusLabel(pass) === 'Redeemed' ? 'Redeemed successfully' : 'Hold near reader / scan QR' }}</p>

          <div class="actions">
            <AppButton variant="ghost" @click="viewPass(pass.id)">View Pass</AppButton>
            <AppButton variant="ghost" @click="copyPassId(pass.id)">Copy Pass ID</AppButton>
            <AppButton variant="ghost" @click="openQr(pass.qr_code)">Open QR</AppButton>
            <AppButton v-if="pass.apple_wallet_url" variant="ghost" @click="openExternal(pass.apple_wallet_url)">Add to Apple Wallet</AppButton>
            <AppButton v-else variant="ghost" disabled>Add to Apple Wallet</AppButton>
            <AppButton v-if="pass.google_wallet_url" variant="ghost" @click="openExternal(pass.google_wallet_url)">Add to Google Wallet</AppButton>
            <AppButton v-else variant="ghost" disabled>Add to Google Wallet</AppButton>
            <AppButton v-if="statusLabel(pass) !== 'Redeemed'" variant="secondary" @click="onRedeem(pass.qr_code)">Redeem</AppButton>
            <AppButton v-if="statusLabel(pass) === 'Redeemed'" variant="ghost" @click="onRestore(pass.id)">Restore</AppButton>
            <AppButton v-if="statusLabel(pass) === 'Active'" variant="ghost" @click="goToScanner(pass.qr_code)">Open scanner</AppButton>
            <AppButton variant="ghost" @click="copyCode(pass.qr_code)">Copy code</AppButton>
            <AppButton variant="ghost" @click="goToSourceDeal(pass.deal_id)">View source deal</AppButton>
          </div>
        </article>
      </div>

    </template>
  </DashboardPageShell>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import DashboardPageShell from "../design-system/patterns/DashboardPageShell.vue";
import PaddedSectionCard from "../design-system/patterns/PaddedSectionCard.vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppErrorState from "../design-system/primitives/AppErrorState.vue";
import AppLoadingState from "../design-system/primitives/AppLoadingState.vue";
import { normalizeWalletPassStatus, walletPassStatusIcon, walletPassStatusLabel, walletPassStatusTone } from "../domain/walletPass";
import { listWalletPasses, redeemWalletPass, restoreWalletPass, type WalletPassPayload } from "../services/api";
import { sessionState } from "../stores/session";
import { showToast } from "../stores/toast";

type Tab = "active" | "redeemed" | "expiring";

const tab = ref<Tab>("active");
const router = useRouter();
const loading = ref(true);
const errorText = ref("");
const passes = ref<WalletPassPayload[]>([]);
const checkoutSyncActive = ref(false);
let baselineCount = 0;
let syncTimer: number | null = null;
let syncTimeout: number | null = null;

const activePasses = computed(() => passes.value.filter((p) => normalizeWalletPassStatus(p.pass_status, p.redemption_status) === "active"));
const redeemedPasses = computed(() => passes.value.filter((p) => normalizeWalletPassStatus(p.pass_status, p.redemption_status) === "redeemed"));
const expiringPasses = computed(() => passes.value.filter((p) => normalizeWalletPassStatus(p.pass_status, p.redemption_status) === "expired"));

const visiblePasses = computed(() => {
  if (tab.value === "redeemed") return redeemedPasses.value;
  if (tab.value === "expiring") return expiringPasses.value;
  return activePasses.value;
});

function formatDate(value: string) {
  return new Date(value).toLocaleString();
}

function statusLabel(pass: WalletPassPayload) {
  return walletPassStatusLabel(normalizeWalletPassStatus(pass.pass_status, pass.redemption_status));
}

function statusTone(pass: WalletPassPayload) {
  return walletPassStatusTone(normalizeWalletPassStatus(pass.pass_status, pass.redemption_status));
}

function statusIcon(pass: WalletPassPayload) {
  return walletPassStatusIcon(normalizeWalletPassStatus(pass.pass_status, pass.redemption_status));
}

function readCheckoutHandoff(): { at?: string } | null {
  try {
    const raw = window.localStorage.getItem("openmat:last-checkout-success");
    if (!raw) return null;
    return JSON.parse(raw) as { at?: string };
  } catch {
    return null;
  }
}

function clearCheckoutHandoff() {
  window.localStorage.removeItem("openmat:last-checkout-success");
}

function maybeStartCheckoutSync() {
  const marker = readCheckoutHandoff();
  if (!marker?.at) return;
  const issuedAt = new Date(marker.at).getTime();
  if (!Number.isFinite(issuedAt)) return;
  const ageMs = Date.now() - issuedAt;
  if (ageMs > 8 * 60 * 1000) {
    clearCheckoutHandoff();
    return;
  }
  checkoutSyncActive.value = true;
  baselineCount = passes.value.length;
  if (syncTimer) window.clearInterval(syncTimer);
  if (syncTimeout) window.clearTimeout(syncTimeout);
  syncTimer = window.setInterval(async () => {
    await load(true);
    if (passes.value.length > baselineCount) {
      showToast("New wallet pass issued successfully.", "success");
      checkoutSyncActive.value = false;
      clearCheckoutHandoff();
      if (syncTimer) window.clearInterval(syncTimer);
      if (syncTimeout) window.clearTimeout(syncTimeout);
      syncTimer = null;
      syncTimeout = null;
    }
  }, 4000);
  syncTimeout = window.setTimeout(() => {
    checkoutSyncActive.value = false;
    clearCheckoutHandoff();
    if (syncTimer) window.clearInterval(syncTimer);
    syncTimer = null;
    syncTimeout = null;
  }, 28000);
}

async function load(silent = false) {
  loading.value = !silent;
  if (!silent) {
    errorText.value = "";
  }
  if (!sessionState.token) {
    loading.value = false;
    errorText.value = "Authentication session expired.";
    return;
  }
  try {
    passes.value = await listWalletPasses(sessionState.token);
  } catch (err) {
    errorText.value = `Failed to load wallet passes: ${String(err)}`;
    showToast(errorText.value, "error");
  } finally {
    loading.value = false;
  }
}

async function onRedeem(qrCode: string) {
  if (!sessionState.token) return;
  try {
    await redeemWalletPass(sessionState.token, qrCode);
    await load();
    showToast("Pass redeemed successfully.", "success");
  } catch (err) {
    errorText.value = `Redeem failed: ${String(err)}`;
    showToast(errorText.value, "error");
  }
}

async function onRestore(passId: string) {
  if (!sessionState.token) return;
  try {
    await restoreWalletPass(sessionState.token, passId);
    await load();
    showToast("Pass restored.", "success");
  } catch (err) {
    errorText.value = `Restore failed: ${String(err)}`;
    showToast(errorText.value, "error");
  }
}

function goToScanner(qrCode: string) {
  void router.push({ path: "/dashboard/redemptions", query: { code: qrCode } });
}

async function copyCode(qrCode: string) {
  try {
    await navigator.clipboard.writeText(qrCode);
    showToast("Pass code copied.", "success");
  } catch {
    showToast("Could not copy pass code.", "error");
  }
}

async function copyPassId(passId: string) {
  try {
    await navigator.clipboard.writeText(passId);
    showToast("Pass ID copied.", "success");
  } catch {
    showToast("Could not copy pass ID.", "error");
  }
}

function openQr(qrCode: string) {
  const url = `https://api.qrserver.com/v1/create-qr-code/?size=320x320&data=${encodeURIComponent(qrCode)}`;
  window.open(url, "_blank", "noopener,noreferrer");
}

function openExternal(url: string) {
  window.open(url, "_blank", "noopener,noreferrer");
}

function viewPass(passId: string) {
  showToast(`Pass ${passId.slice(0, 8)} ready`, "info");
}

function goToSourceDeal(dealId: string) {
  void router.push({ path: "/dashboard/deals", query: { deal: dealId } });
}

onMounted(async () => {
  await load();
  maybeStartCheckoutSync();
});

onBeforeUnmount(() => {
  if (syncTimer) window.clearInterval(syncTimer);
  if (syncTimeout) window.clearTimeout(syncTimeout);
});
</script>

<style scoped>
.chips { display: flex; flex-wrap: wrap; gap: 12px; }
.chip { border-radius: 999px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.03); color: rgba(255,255,255,.75); padding: 8px 12px; font-size: 12px; font-weight: 600; letter-spacing: .02em; }
.chip.is-active { border-color: rgba(240,190,100,.5); background: rgba(240,190,100,.15); color: #f4d8a7; }
.sync-card { border: 1px solid rgba(113,182,255,.45); background: rgba(113,182,255,.08); }
.sync-card p { margin: 6px 0 0; color: rgba(255,255,255,.7); }
.empty-state { border-radius: 16px; border: 1px dashed rgba(255,255,255,.22); text-align: center; }
.empty-state h2 { margin: 0; font-size: 30px; line-height: 1.15; letter-spacing: -0.02em; }
.empty-state p { margin: 8px 0 0; color: rgba(255,255,255,.62); font-size: 15px; line-height: 1.45; }
.pass-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 20px; }
.pass-card { border-radius: 18px; border: 1px solid rgba(255,255,255,.1); background: linear-gradient(180deg, rgba(14,22,35,.78), rgba(10,16,30,.72)); padding: 16px; transition: transform 180ms ease, box-shadow 180ms ease; }
.pass-card:hover { transform: translateY(-2px); box-shadow: 0 14px 38px rgba(0,0,0,.28); }
.pass-top { display: flex; justify-content: space-between; align-items: center; }
.pass-id { margin: 0; color: rgba(255,255,255,.58); font-size: 12px; }
.status { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .08em; }
.status.is-green { color: #52d58b; }
.status.is-red { color: #f08a6b; }
.status.is-amber { color: #f4d8a7; }
.status.is-cyan { color: #9fd0ff; }
.pass-card h3 { margin: 10px 0 0; font-size: 21px; }
.meta { margin: 6px 0 0; color: rgba(255,255,255,.64); font-size: 13px; }
.qr { margin-top: 12px; height: 88px; border-radius: 12px; background: rgba(255,255,255,.95); color: #111; display: grid; place-items: center; font-size: 30px; }
.hint { margin: 8px 0 0; color: rgba(255,255,255,.6); font-size: 12px; }
.actions { margin-top: 10px; display: flex; gap: 8px; flex-wrap: wrap; }
@media (max-width: 1180px) { .pass-grid { grid-template-columns: repeat(2, minmax(0,1fr)); } }
@media (max-width: 767px) {
  .pass-grid { grid-template-columns: 1fr; }
}
</style>
