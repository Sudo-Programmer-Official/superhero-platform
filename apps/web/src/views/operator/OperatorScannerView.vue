<template>
  <section class="scanner-shell">
    <article class="summary-card">
      <div>
        <p class="eyebrow">Today redeemed</p>
        <strong>{{ todayRedeemed }}</strong>
      </div>
      <div>
        <p class="eyebrow">Pending arrivals</p>
        <strong>{{ pendingArrivals }}</strong>
      </div>
    </article>

    <article class="scanner-card">
      <header class="scanner-top">
        <h1>Redemptions</h1>
        <button class="top-btn" type="button" @click="goWallet">Deals</button>
      </header>
      <div v-if="scannerState === 'idle'" class="state">
        <p class="title">Scan pass</p>
        <p class="sub">Point camera at the wallet QR to check in instantly.</p>
        <button class="btn primary" type="button" @click="requestCameraAndScan">Scan Pass</button>
      </div>

      <div v-else-if="scannerState === 'requesting_camera'" class="state">
        <p class="title">Requesting camera access…</p>
      </div>

      <div v-else-if="scannerState === 'scanning'" class="state">
        <div class="camera-wrap">
          <video ref="scannerVideo" class="camera-video" playsinline muted autoplay></video>
          <div class="overlay">
            <div class="corner tl"></div>
            <div class="corner tr"></div>
            <div class="corner bl"></div>
            <div class="corner br"></div>
            <div class="frame">
              <div class="line"></div>
            </div>
          </div>
        </div>
        <p class="sub">Align QR inside frame</p>
        <p v-if="scannerError" class="sub warn">{{ scannerError }}</p>
        <div class="row">
          <button class="btn" type="button" @click="simulateScan">Simulate</button>
          <button class="btn" type="button" @click="reset">Retry</button>
          <button class="btn" type="button" @click="goWallet">Back to Deals</button>
        </div>
      </div>

      <div v-else-if="scannerState === 'validating'" class="state">
        <p class="title">Validating pass…</p>
      </div>

      <div v-else-if="scannerState === 'success' && result" class="state success">
        <p class="icon">✅</p>
        <p class="title">Checked In</p>
        <p class="sub strong">{{ result.attendeeName }}</p>
        <p class="sub">{{ result.eventName }}</p>
        <p class="sub">{{ formatTime(result.redeemedAt) }}</p>
        <div class="row">
          <button class="btn primary" type="button" @click="reset">Scan Next</button>
          <button class="btn" type="button" @click="goWallet">Back to Deals</button>
        </div>
      </div>

      <div v-else-if="scannerState === 'already_redeemed'" class="state warning">
        <p class="title">Already redeemed</p>
        <p class="sub">{{ statusNote || 'This pass was previously checked in.' }}</p>
        <div class="row">
          <button class="btn" type="button" @click="reset">Retry scan</button>
          <button class="btn" type="button" @click="goWallet">Back to Deals</button>
        </div>
      </div>

      <div v-else-if="scannerState === 'expired'" class="state warning">
        <p class="title">Pass expired</p>
        <p class="sub">{{ statusNote }}</p>
        <div class="row">
          <button class="btn" type="button" @click="reset">Retry scan</button>
          <button class="btn" type="button" @click="goWallet">Back to Deals</button>
        </div>
      </div>

      <div v-else class="state error">
        <p class="title">Pass not recognized</p>
        <p class="sub">{{ statusNote || 'Unable to validate this pass.' }}</p>
        <div class="row">
          <button class="btn" type="button" @click="reset">Retry scan</button>
          <button class="btn" type="button" @click="goWallet">Back to Deals</button>
        </div>
      </div>
    </article>

    <article class="manual-card">
      <p class="manual-title">Manual code entry</p>
      <div class="manual-row">
        <input v-model="manualCode" type="text" placeholder="Enter attendee pass code" />
        <button class="btn primary" type="button" :disabled="!canSubmitManual" @click="redeemCode(manualCode)">
          {{ isSubmitting ? 'Validating…' : 'Redeem' }}
        </button>
      </div>
    </article>

    <article class="activity-card">
      <div class="activity-head">
        <p class="manual-title">Recent activity</p>
        <button class="top-btn" type="button" @click="loadActivity" :disabled="activityLoading">Refresh</button>
      </div>
      <p v-if="activityLoading" class="sub">Loading activity…</p>
      <p v-else-if="activityItems.length === 0" class="sub">No redemption activity yet.</p>
      <div v-else class="activity-list">
        <article v-for="item in activityItems" :key="item.id" class="activity-row">
          <p>{{ item.label }}</p>
          <span>{{ item.time }}</span>
        </article>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from "vue";
import { useRouter } from "vue-router";
import { activityLabel, activityTime, type ActivityEvent } from "../../domain/activity";
import { useRedemptionFlow } from "../../composables/useRedemptionFlow";
import { listActivityEvents } from "../../services/api";
import { sessionState } from "../../stores/session";

const router = useRouter();
const {
  canSubmitManual,
  isSubmitting,
  manualCode,
  redeemCode,
  requestCameraAndScan,
  reset,
  result,
  scannerState,
  scannerError,
  statusNote,
  setVideoElement,
  simulateScan,
  teardownScanner
} = useRedemptionFlow();

const scannerVideo = useTemplateRef<HTMLVideoElement>("scannerVideo");
const activityLoading = ref(false);
const activityEvents = ref<ActivityEvent[]>([]);
const activityItems = computed(() => activityEvents.value.slice(0, 6).map((item) => ({ id: item.id, label: activityLabel(item), time: activityTime(item.created_at) })));
const todayRedeemed = computed(() => activityEvents.value.filter((item) => item.event_type === "redemption.success").length);
const pendingArrivals = computed(() => Math.max(0, 12 - todayRedeemed.value));

function goWallet() {
  void router.push({ name: "app-deals" });
}

function formatTime(value: string): string {
  return new Date(value).toLocaleString();
}

watch(scannerVideo, (el) => {
  setVideoElement(el ?? null);
});

async function loadActivity() {
  if (!sessionState.token) return;
  activityLoading.value = true;
  try {
    const page = await listActivityEvents(sessionState.token);
    activityEvents.value = page.items.filter((item) => item.event_type.startsWith("redemption."));
  } finally {
    activityLoading.value = false;
  }
}

onMounted(() => {
  void loadActivity();
});

onBeforeUnmount(() => {
  teardownScanner();
});
</script>

<style scoped>
.scanner-shell { display: grid; gap: var(--mvp-gap, 14px); padding-bottom: 80px; }
.summary-card {
  border: 1px solid rgba(255,255,255,.12);
  border-radius: var(--mvp-radius, 16px);
  background: rgba(10,20,36,.72);
  padding: var(--mvp-card-pad, 16px);
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.summary-card strong { font-size: 30px; letter-spacing: -.02em; }
.eyebrow { margin: 0; color: rgba(230,238,249,.68); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
.scanner-top { display: grid; grid-template-columns: 1fr auto; gap: 8px; align-items: center; margin-bottom: 10px; }
.scanner-top h1 { margin: 0; font-size: 24px; }
.top-btn { min-height: var(--mvp-btn-h, 44px); border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 10px; }
.scanner-card { border: 1px solid rgba(255,255,255,.12); border-radius: var(--mvp-radius, 16px); background: rgba(10,20,36,.72); padding: var(--mvp-card-pad, 16px); }
.state { display: grid; gap: 10px; }
.title { margin: 0; font-size: 22px; font-weight: 700; }
.sub { margin: 0; color: rgba(230,238,249,.74); }
.sub.strong { color: #e8eef8; font-weight: 600; }
.icon { margin: 0; font-size: 34px; }
.camera-wrap { position: relative; height: min(64dvh, 520px); border-radius: 16px; border: 1px solid rgba(255,255,255,.16); overflow: hidden; background: radial-gradient(circle at 50% 20%, rgba(113,182,255,.18), rgba(9,15,26,.86)); }
.camera-video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: .6; }
.overlay { position: absolute; inset: 0; display: grid; place-items: center; }
.frame { width: min(70vw, 280px); height: min(70vw, 280px); border: 2px solid rgba(240,190,100,.72); border-radius: 16px; box-shadow: 0 0 0 1px rgba(240,190,100,.12), 0 0 26px rgba(240,190,100,.18); overflow: hidden; position: relative; }
.line { position: absolute; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, rgba(82,213,139,0), rgba(82,213,139,.95), rgba(82,213,139,0)); animation: scan 2.1s ease-in-out infinite; }
.corner { position: absolute; width: 28px; height: 28px; border-color: rgba(240,190,100,.95); border-style: solid; }
.tl { top: calc(50% - min(35vw, 140px)); left: calc(50% - min(35vw, 140px)); border-width: 3px 0 0 3px; border-radius: 12px 0 0 0; transform: translate(-10px, -10px); }
.tr { top: calc(50% - min(35vw, 140px)); right: calc(50% - min(35vw, 140px)); border-width: 3px 3px 0 0; border-radius: 0 12px 0 0; transform: translate(10px, -10px); }
.bl { bottom: calc(50% - min(35vw, 140px)); left: calc(50% - min(35vw, 140px)); border-width: 0 0 3px 3px; border-radius: 0 0 0 12px; transform: translate(-10px, 10px); }
.br { bottom: calc(50% - min(35vw, 140px)); right: calc(50% - min(35vw, 140px)); border-width: 0 3px 3px 0; border-radius: 0 0 12px 0; transform: translate(10px, 10px); }
.row { display: flex; gap: 8px; flex-wrap: wrap; }
.btn { min-height: var(--mvp-btn-h, 44px); border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.warning .title { color: #f4d8a7; }
.error .title { color: #ffb2b2; }
.success .title { color: #75ecad; }
.manual-card { border: 1px solid rgba(255,255,255,.12); border-radius: var(--mvp-radius, 16px); background: rgba(10,20,36,.72); padding: var(--mvp-card-pad, 16px); display: grid; gap: 10px; }
.manual-title { margin: 0; font-size: 14px; color: #f4d8a7; letter-spacing: .06em; text-transform: uppercase; }
.activity-card { border: 1px solid rgba(255,255,255,.12); border-radius: var(--mvp-radius, 16px); background: rgba(10,20,36,.72); padding: var(--mvp-card-pad, 16px); display: grid; gap: 10px; }
.activity-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.activity-list { display: grid; gap: 8px; }
.activity-row {
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 10px;
  background: rgba(255,255,255,.03);
  padding: 10px;
  display: flex;
  justify-content: space-between;
  gap: 10px;
}
.activity-row p { margin: 0; }
.activity-row span { margin: 0; color: rgba(230,238,249,.66); font-size: 12px; }
.manual-row { display: grid; gap: 8px; grid-template-columns: 1fr; }
.manual-row input { min-height: var(--mvp-btn-h, 44px); border: 1px solid rgba(255,255,255,.14); border-radius: 10px; background: rgba(255,255,255,.04); color: #e8eef8; padding: 0 12px; box-sizing: border-box; }
@media (min-width: 640px) {
  .manual-row { grid-template-columns: 1fr auto; }
}
@keyframes scan { 0% { top: 8px; } 50% { top: calc(100% - 10px); } 100% { top: 8px; } }
</style>
