<template>
  <section class="stack">
    <article class="card">
      <p class="eyebrow">Wallet</p>
      <h2>Pass activity</h2>
      <div class="stats">
        <p><span>Active</span><strong>{{ activePasses.length }}</strong></p>
        <p><span>Redeemed</span><strong>{{ redeemedPasses.length }}</strong></p>
        <p><span>Expired</span><strong>{{ expiredPasses.length }}</strong></p>
      </div>
      <div class="row">
        <button class="btn primary" @click="goScanner">Open Scanner</button>
        <button class="btn" @click="refresh">Refresh</button>
      </div>
    </article>

    <article class="card">
      <div class="chips">
        <button class="chip" :class="{ 'is-active': tab === 'active' }" @click="tab='active'">Active</button>
        <button class="chip" :class="{ 'is-active': tab === 'redeemed' }" @click="tab='redeemed'">Redeemed</button>
        <button class="chip" :class="{ 'is-active': tab === 'expired' }" @click="tab='expired'">Expired</button>
      </div>

      <div v-if="loading" class="skeleton-list">
        <div v-for="n in 3" :key="n" class="skeleton shimmer"></div>
      </div>
      <p v-else-if="errorText" class="hint is-error">{{ errorText }}</p>
      <div v-else-if="visible.length" class="items">
        <article v-for="pass in visible" :key="pass.id" class="item" :class="`state-${state(pass)}`">
          <div class="item-top">
            <p class="id">#{{ pass.id.slice(0, 8) }}</p>
            <span class="state-chip">{{ state(pass) }}</span>
          </div>
          <p class="title">{{ pass.deal_title || `Deal ${pass.deal_id.slice(0, 8)}` }}</p>
          <p class="meta">{{ pass.attendee_email || "Guest" }}</p>
          <p class="meta" v-if="state(pass) === 'active'">Ready for check-in</p>
          <p class="meta" v-if="state(pass) === 'redeemed'">Checked in successfully</p>
          <div class="actions">
            <button class="btn" @click="copyCode(pass.qr_code)">Copy QR</button>
            <button class="btn" @click="showQr(pass.qr_code)">Fullscreen QR</button>
          </div>
        </article>
      </div>
      <p v-else class="hint">No passes in this state yet.</p>
    </article>

    <div v-if="qrModal" class="qr-overlay" @click.self="qrModal = null">
      <section class="qr-sheet" role="dialog" aria-modal="true" aria-label="Fullscreen QR">
        <div class="qr-head">
          <p>Scan at check-in</p>
          <button class="btn" type="button" @click="qrModal = null">Close</button>
        </div>
        <img :src="qrUrl(qrModal)" alt="Pass QR code" class="qr-image" />
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { listWalletPasses, type WalletPassPayload } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";
import { normalizeWalletPassStatus } from "../../domain/walletPass";

type Tab = "active" | "redeemed" | "expired";

const router = useRouter();
const tab = ref<Tab>("active");
const passes = ref<WalletPassPayload[]>([]);
const loading = ref(false);
const errorText = ref("");
const qrModal = ref<string | null>(null);

const activePasses = computed(() => passes.value.filter((p) => normalizeWalletPassStatus(p.pass_status, p.redemption_status) === "active"));
const redeemedPasses = computed(() => passes.value.filter((p) => normalizeWalletPassStatus(p.pass_status, p.redemption_status) === "redeemed"));
const expiredPasses = computed(() => passes.value.filter((p) => normalizeWalletPassStatus(p.pass_status, p.redemption_status) === "expired"));

const visible = computed(() => {
  if (tab.value === "redeemed") return redeemedPasses.value;
  if (tab.value === "expired") return expiredPasses.value;
  return activePasses.value;
});

function state(pass: WalletPassPayload): "active" | "redeemed" | "expired" {
  return normalizeWalletPassStatus(pass.pass_status, pass.redemption_status);
}

async function refresh() {
  if (!sessionState.token) return;
  loading.value = true;
  errorText.value = "";
  try {
    passes.value = await listWalletPasses(sessionState.token);
  } catch (err) {
    errorText.value = `Failed to load passes: ${String(err)}`;
  } finally {
    loading.value = false;
  }
}

function goScanner() {
  void router.push({ name: "redemptions", query: { mode: "operator" } });
}

async function copyCode(code: string) {
  await navigator.clipboard.writeText(code);
  showToast("QR code copied.", "success");
}

function qrUrl(code: string | null): string {
  return `https://api.qrserver.com/v1/create-qr-code/?size=480x480&data=${encodeURIComponent(code || "")}`;
}

function showQr(code: string) {
  qrModal.value = code;
}

onMounted(() => {
  void refresh();
});
</script>

<style scoped>
.stack { display: grid; gap: var(--mvp-gap, 14px); padding-bottom: 12px; }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: var(--mvp-radius, 16px); background: rgba(10,20,36,.72); padding: var(--mvp-card-pad, 16px); display: grid; gap: 12px; }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
h2 { margin: 0; font-size: 24px; line-height: 1.05; }
.stats { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 8px; }
.stats p { margin: 0; border: 1px solid rgba(255,255,255,.12); border-radius: 10px; background: rgba(255,255,255,.04); padding: 10px; display: grid; gap: 4px; }
.stats span { font-size: 12px; color: rgba(230,238,249,.72); }
.stats strong { font-size: 20px; }
.row { display: flex; gap: 8px; flex-wrap: wrap; }
.btn { min-height: var(--mvp-btn-h, 44px); border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.chips { display: flex; gap: 8px; flex-wrap: wrap; }
.chip { min-height: 38px; border-radius: 999px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.04); color: rgba(230,238,249,.8); padding: 0 12px; }
.chip.is-active { border-color: rgba(240,190,100,.45); color: #f4d8a7; background: rgba(240,190,100,.12); }
.items { display: grid; gap: 10px; }
.item { border: 1px solid rgba(255,255,255,.1); border-radius: 12px; background: rgba(8,14,24,.72); padding: 10px; display: grid; gap: 8px; }
.item.state-active { border-color: rgba(82,213,139,.4); box-shadow: inset 0 0 0 1px rgba(82,213,139,.2); }
.item.state-redeemed { border-color: rgba(113,182,255,.45); }
.item.state-expired { border-color: rgba(255,120,120,.4); }
.item-top { display: flex; align-items: center; justify-content: space-between; }
.state-chip { border-radius: 999px; border: 1px solid rgba(255,255,255,.2); padding: 4px 8px; text-transform: uppercase; font-size: 11px; color: rgba(230,238,249,.82); }
.id { margin: 0; font-weight: 650; }
.title { margin: 0; font-weight: 600; }
.meta { margin: 0; color: rgba(230,238,249,.72); font-size: 13px; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.hint { margin: 0; color: rgba(230,238,249,.72); font-size: 13px; }
.hint.is-error { color: #ffb2b2; }
.qr-overlay { position: fixed; inset: 0; z-index: 35; background: rgba(4,10,20,.64); backdrop-filter: blur(6px); display: grid; align-items: end; }
.qr-sheet { border-radius: 20px 20px 0 0; border: 1px solid rgba(255,255,255,.14); border-bottom: none; background: rgba(7,14,24,.98); padding: 14px; display: grid; gap: 12px; }
.qr-head { display: flex; align-items: center; justify-content: space-between; }
.qr-head p { margin: 0; color: #f4d8a7; }
.qr-image { width: 100%; max-width: 420px; margin: 0 auto; border-radius: 14px; background: #fff; padding: 10px; box-sizing: border-box; }
.skeleton-list { display: grid; gap: 8px; }
.skeleton { height: 92px; border-radius: 12px; border: 1px solid rgba(255,255,255,.08); background: rgba(255,255,255,.04); }
.shimmer { background-image: linear-gradient(100deg, rgba(255,255,255,.03) 20%, rgba(255,255,255,.1) 50%, rgba(255,255,255,.03) 80%); background-size: 200% 100%; animation: shimmer 1.5s linear infinite; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>
