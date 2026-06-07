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
      <p class="eyebrow">Redemptions</p>
      <h1>Open Scanner</h1>
      <p class="sub">Check in customers by scanning the pass QR.</p>

      <div v-if="scannerState === 'idle'" class="state">
        <button class="btn primary" type="button" @click="requestCameraAndScan">Open Scanner</button>
      </div>

      <div v-else-if="scannerState === 'requesting_camera'" class="state">
        <p class="title">Requesting camera access…</p>
      </div>

      <div v-else-if="scannerState === 'scanning'" class="state">
        <div class="camera-wrap">
          <video ref="scannerVideo" class="camera-video" playsinline muted autoplay></video>
          <div class="overlay">
            <div class="frame">
              <div class="line"></div>
            </div>
          </div>
        </div>
        <p class="sub">Align the pass QR inside the frame.</p>
        <p v-if="scannerError" class="sub warn">{{ scannerError }}</p>
        <div class="scan-actions">
          <button class="btn" type="button" @click="simulateScan">Simulate scan</button>
          <button class="btn" type="button" @click="reset">Cancel</button>
        </div>
      </div>

      <div v-else-if="scannerState === 'validating'" class="state">
        <p class="title">Validating pass…</p>
      </div>

      <div v-else-if="scannerState === 'success' && result" class="state result-state success">
        <p class="result-label">Valid</p>
        <p class="result-name">{{ result.attendeeName }}</p>
        <p class="result-deal">{{ result.eventName }}</p>
        <p class="result-time">{{ formatTime(result.redeemedAt) }}</p>
        <button class="btn primary" type="button" @click="reset">Scan next pass</button>
      </div>

      <div v-else-if="scannerState === 'already_redeemed'" class="state result-state warning">
        <p class="result-label">Already redeemed</p>
        <p class="result-deal">{{ statusNote || 'This pass was previously checked in.' }}</p>
        <button class="btn" type="button" @click="reset">Try another pass</button>
      </div>

      <div v-else-if="scannerState === 'expired'" class="state result-state warning">
        <p class="result-label">Pass expired</p>
        <p class="result-deal">{{ statusNote }}</p>
        <button class="btn" type="button" @click="reset">Try another pass</button>
      </div>

      <div v-else class="state result-state error">
        <p class="result-label">Invalid pass</p>
        <p class="result-deal">{{ statusNote || 'Unable to validate this code.' }}</p>
        <button class="btn" type="button" @click="reset">Try another pass</button>
      </div>
    </article>

    <details class="manual-card">
      <summary>More options</summary>
      <div class="manual-body">
        <p class="manual-title">Manual code entry</p>
        <div class="manual-row">
          <input v-model="manualCode" type="text" placeholder="Enter attendee pass code" />
          <button class="btn primary" type="button" :disabled="!canSubmitManual" @click="redeemCode(manualCode)">
            {{ isSubmitting ? 'Validating…' : 'Redeem' }}
          </button>
        </div>
      </div>
    </details>

    <article class="activity-card">
      <div class="activity-head">
        <p class="eyebrow">Recent redemptions</p>
        <button class="btn" type="button" @click="loadActivity" :disabled="activityLoading">Refresh</button>
      </div>
      <p v-if="activityLoading" class="sub">Loading activity…</p>
      <p v-else-if="activityItems.length === 0" class="sub">No redemption activity yet.</p>
      <div v-else class="activity-list">
        <article v-for="item in activityItems" :key="item.id" class="activity-row">
          <div>
            <p class="activity-customer">{{ item.customer }}</p>
            <p class="activity-deal">{{ item.deal }}</p>
          </div>
          <span>{{ item.time }}</span>
        </article>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, useTemplateRef, watch } from "vue";
import { activityTime, type ActivityEvent } from "../../domain/activity";
import { useRedemptionFlow } from "../../composables/useRedemptionFlow";
import { listActivityEvents } from "../../services/api";
import { sessionState } from "../../stores/session";

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

const activityItems = computed(() =>
  activityEvents.value.slice(0, 6).map((item) => ({
    id: item.id,
    customer: String(item.metadata.customer_name || item.metadata.attendee_name || "Customer"),
    deal: String(item.metadata.deal_title || item.metadata.deal_name || "Deal"),
    time: activityTime(item.created_at)
  }))
);
const todayRedeemed = computed(() => activityEvents.value.filter((item) => item.event_type === "redemption.success").length);
const pendingArrivals = computed(() => Math.max(0, 12 - todayRedeemed.value));

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
.scanner-shell { display: grid; gap: 14px; padding-bottom: calc(108px + env(safe-area-inset-bottom, 0px)); }
.summary-card {
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  background: rgba(10,20,36,.72);
  padding: 16px;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}
.summary-card strong { font-size: 30px; letter-spacing: -.02em; }
.eyebrow { margin: 0; color: rgba(230,238,249,.68); font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
.scanner-card, .activity-card {
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  background: rgba(10,20,36,.72);
  padding: 16px;
  display: grid;
  gap: 10px;
}
h1 { margin: 0; font-size: 28px; line-height: 1.06; }
.sub { margin: 0; color: rgba(230,238,249,.74); }
.state { display: grid; gap: 10px; }
.title { margin: 0; font-size: 22px; font-weight: 700; }
.camera-wrap {
  position: relative;
  height: min(62dvh, 520px);
  border-radius: 18px;
  border: 1px solid rgba(255,255,255,.16);
  overflow: hidden;
  background: radial-gradient(circle at 50% 20%, rgba(113,182,255,.18), rgba(9,15,26,.86));
}
.camera-video { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; opacity: .6; }
.overlay { position: absolute; inset: 0; display: grid; place-items: center; }
.frame {
  width: min(70vw, 280px);
  height: min(70vw, 280px);
  border: 2px solid rgba(240,190,100,.72);
  border-radius: 16px;
  box-shadow: 0 0 0 1px rgba(240,190,100,.12), 0 0 26px rgba(240,190,100,.18);
  overflow: hidden;
  position: relative;
}
.line { position: absolute; left: 0; right: 0; height: 2px; background: linear-gradient(90deg, rgba(82,213,139,0), rgba(82,213,139,.95), rgba(82,213,139,0)); animation: scan 2.1s ease-in-out infinite; }
.btn {
  min-height: 44px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.05);
  color: #e8eef8;
  padding: 0 12px;
}
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.scan-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.result-state { gap: 8px; }
.result-label { margin: 0; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; color: #f4d8a7; }
.result-name { margin: 0; font-size: 24px; font-weight: 700; line-height: 1.05; }
.result-deal, .result-time { margin: 0; color: rgba(230,238,249,.74); }
.manual-card {
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  background: rgba(10,20,36,.72);
  padding: 16px;
}
.manual-card summary { cursor: pointer; color: #f4d8a7; font-size: 12px; text-transform: uppercase; letter-spacing: .1em; list-style: none; }
.manual-card summary::-webkit-details-marker { display: none; }
.manual-body { margin-top: 12px; display: grid; gap: 10px; }
.manual-title { margin: 0; font-size: 14px; color: rgba(230,238,249,.72); text-transform: uppercase; letter-spacing: .08em; }
.manual-row { display: grid; gap: 8px; grid-template-columns: 1fr; }
.manual-row input {
  min-height: 44px;
  border: 1px solid rgba(255,255,255,.14);
  border-radius: 10px;
  background: rgba(255,255,255,.04);
  color: #e8eef8;
  padding: 0 12px;
  box-sizing: border-box;
}
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
.activity-customer { font-weight: 650; }
.activity-deal { color: rgba(230,238,249,.66); font-size: 13px; }
.activity-row span { color: rgba(230,238,249,.66); font-size: 12px; white-space: nowrap; }
.warn { color: #f4d8a7; }
.error .result-label { color: #ffb2b2; }
.success .result-label { color: #7ce9af; }
@media (min-width: 640px) {
  .manual-row { grid-template-columns: 1fr auto; }
}
@keyframes scan { 0% { top: 8px; } 50% { top: calc(100% - 10px); } 100% { top: 8px; } }
</style>
