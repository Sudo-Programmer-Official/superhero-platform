<template>
  <section class="redemptions">
    <header class="redemptions__head">
      <div>
        <p class="eyebrow">Redemption Operations</p>
        <h1>Scan and Redeem</h1>
        <p>Point camera at QR code or Apple Wallet pass.</p>
      </div>
      <span class="state-pill" :class="`is-${scannerState}`">{{ stateLabel }}</span>
    </header>

    <div class="redemptions__grid">
      <AppCard class="scanner-card">
        <h2>Scanner</h2>

        <div v-if="scannerState === 'idle'" class="scanner-state">
          <p class="helper">Ready to validate a customer pass in under a second.</p>
          <AppButton variant="primary" size="form" @click="requestCameraAndScan">Scan pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'requesting_camera'" class="scanner-state">
          <p class="helper">Requesting camera access…</p>
        </div>

        <div v-else-if="scannerState === 'scanning'" class="scanner-state">
          <div class="camera-placeholder">
            <video ref="scannerVideo" class="camera-video" playsinline muted autoplay></video>
            <div class="camera-overlay">
              <div class="corner corner--tl"></div>
              <div class="corner corner--tr"></div>
              <div class="corner corner--bl"></div>
              <div class="corner corner--br"></div>
              <div class="scan-frame">
                <div class="scan-line"></div>
              </div>
            </div>
            <p>Live camera preview</p>
          </div>

          <p class="helper">Align the pass QR inside the frame to auto-validate.</p>
          <p v-if="scannerError" class="helper helper--warning">{{ scannerError }}</p>
          <p v-if="!canUseNativeDetector" class="helper helper--warning">Auto QR detect is limited in this browser. Use manual fallback if needed.</p>

          <div class="scanner-actions">
            <AppButton variant="secondary" size="form" @click="simulateScan">Simulate scan</AppButton>
            <AppButton variant="ghost" size="form" @click="reset">Cancel</AppButton>
          </div>
        </div>

        <div v-else-if="scannerState === 'validating'" class="scanner-state">
          <p class="helper">Validating pass and checking redemption status…</p>
        </div>

        <div v-else-if="scannerState === 'success' && result" class="scanner-state state-success">
          <div class="result-card result-card--success">
            <div class="checkmark">✓</div>
            <h3>Redeemed</h3>
            <p><strong>{{ result.attendeeName }}</strong></p>
            <p>{{ result.eventName }}</p>
            <p class="timestamp">{{ formatTime(result.redeemedAt) }}</p>
          </div>
          <AppButton variant="primary" size="form" @click="reset">Scan next pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'already_redeemed'" class="scanner-state state-warning">
          <div class="result-card result-card--warning">
            <h3>Already redeemed</h3>
            <p>This pass was previously redeemed.</p>
            <p class="timestamp">Check history for latest timestamp.</p>
          </div>
          <AppButton variant="secondary" size="form" @click="reset">Try another pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'expired'" class="scanner-state state-warning">
          <div class="result-card result-card--warning">
            <h3>Pass expired</h3>
            <p>This pass cannot be redeemed anymore.</p>
          </div>
          <AppButton variant="secondary" size="form" @click="reset">Try another pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'invalid'" class="scanner-state state-error">
          <div class="result-card result-card--error">
            <h3>Invalid pass</h3>
            <p>We could not verify this code.</p>
          </div>
          <AppButton variant="secondary" size="form" @click="reset">Try another pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'offline'" class="scanner-state state-error">
          <div class="result-card result-card--error">
            <h3>Offline / session issue</h3>
            <p>Check network and auth session, then retry.</p>
          </div>
          <AppButton variant="secondary" size="form" @click="reset">Retry</AppButton>
        </div>
      </AppCard>

      <AppCard class="manual-card">
        <h2>Manual fallback</h2>
        <p class="muted">If camera access is denied, enter redemption code manually.</p>

        <div class="manual-grid">
          <AppInput v-model="manualCode" placeholder="Enter redemption code" />
          <AppButton variant="primary" size="form" :disabled="!canSubmitManual" @click="redeemCode(manualCode)">
            {{ isSubmitting ? "Validating..." : "Redeem manually" }}
          </AppButton>
        </div>

        <div class="permission-note">
          <p><strong>Camera permission:</strong> {{ cameraPermission }}</p>
        </div>
      </AppCard>

      <AppCard class="history-card">
        <div class="history-head">
          <h2>Recent redemptions</h2>
          <span>{{ history.length }}</span>
        </div>

        <div class="history-list">
          <article v-for="item in history" :key="item.id" class="history-item">
            <div class="avatar">{{ item.avatarInitials }}</div>
            <div>
              <p class="name">{{ item.attendeeName }}</p>
              <p class="event">{{ item.eventName }}</p>
            </div>
            <div class="meta">
              <span class="chip" :class="`chip--${item.status}`">{{ item.status.replace('_', ' ') }}</span>
              <p>{{ formatTime(item.timestamp) }}</p>
            </div>
          </article>
        </div>
      </AppCard>
    </div>

    <transition name="toast-fade">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </section>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, useTemplateRef, watch } from "vue";
import { useRoute } from "vue-router";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import AppInput from "../design-system/primitives/AppInput.vue";
import { useRedemptionFlow } from "../composables/useRedemptionFlow";

const route = useRoute();
const {
  cameraPermission,
  canSubmitManual,
  canUseNativeDetector,
  history,
  hydrateMockHistory,
  isSubmitting,
  manualCode,
  redeemCode,
  requestCameraAndScan,
  reset,
  result,
  scannerState,
  scannerError,
  setVideoElement,
  setToast,
  simulateScan,
  stateLabel,
  teardownScanner,
  toast
} = useRedemptionFlow();
const scannerVideo = useTemplateRef<HTMLVideoElement>("scannerVideo");

function formatTime(value: string): string {
  return new Date(value).toLocaleString();
}

onMounted(() => {
  hydrateMockHistory();
  const prefillCode = String(route.query.code || "").trim();
  if (prefillCode) {
    manualCode.value = prefillCode;
    setToast("Pass code prefilled. Tap Redeem manually to continue.");
  }
});

watch(scannerVideo, (el) => {
  setVideoElement(el ?? null);
});

onBeforeUnmount(() => {
  teardownScanner();
});
</script>

<style scoped>
.redemptions { padding: 18px; display: grid; gap: 12px; }
.redemptions__head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.redemptions__head h1 { margin: 6px 0 0; font-size: clamp(30px, 4vw, 46px); }
.redemptions__head p { margin: 8px 0 0; color: rgba(255,255,255,.66); }
.state-pill { border-radius: 999px; border: 1px solid rgba(255,255,255,.2); padding: 7px 12px; text-transform: uppercase; letter-spacing: .08em; font-size: 11px; color: rgba(255,255,255,.82); }
.state-pill.is-success { border-color: rgba(82,213,139,.55); color: #52d58b; }
.state-pill.is-invalid, .state-pill.is-offline { border-color: rgba(255,120,120,.6); color: #ff9a9a; }
.state-pill.is-already_redeemed, .state-pill.is-expired { border-color: rgba(240,190,100,.5); color: #f4d8a7; }
.redemptions__grid {
  display: grid;
  grid-template-columns: minmax(0, 1fr) minmax(0, 420px);
  grid-template-areas:
    "scanner manual"
    "scanner history";
  gap: 12px;
}
.scanner-card { grid-area: scanner; }
.manual-card { grid-area: manual; }
.history-card { grid-area: history; }
.scanner-state { display: grid; gap: 10px; margin-top: 8px; }
.helper { margin: 0; color: rgba(255,255,255,.72); }
.helper--warning { color: #f4d8a7; }
.camera-placeholder {
  position: relative;
  height: 340px;
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,.16);
  background: radial-gradient(circle at 50% 20%, rgba(113,182,255,.18), rgba(9,15,26,.86));
  display: grid;
  place-items: center;
  color: rgba(255,255,255,.62);
  overflow: hidden;
}
.camera-video {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0.58;
}
.camera-overlay { position: relative; width: 220px; height: 220px; }
.scan-frame {
  position: absolute;
  inset: 0;
  border: 2px solid rgba(240,190,100,.72);
  border-radius: 16px;
  box-shadow: 0 0 0 1px rgba(240,190,100,.12), 0 0 26px rgba(240,190,100,.18);
  overflow: hidden;
}
.scan-line {
  position: absolute;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, rgba(82,213,139,0), rgba(82,213,139,.95), rgba(82,213,139,0));
  animation: scan 2.1s ease-in-out infinite;
}
.corner {
  position: absolute;
  width: 28px;
  height: 28px;
  border-color: rgba(240,190,100,.95);
  border-style: solid;
}
.corner--tl { top: -2px; left: -2px; border-width: 3px 0 0 3px; border-radius: 12px 0 0 0; }
.corner--tr { top: -2px; right: -2px; border-width: 3px 3px 0 0; border-radius: 0 12px 0 0; }
.corner--bl { bottom: -2px; left: -2px; border-width: 0 0 3px 3px; border-radius: 0 0 0 12px; }
.corner--br { bottom: -2px; right: -2px; border-width: 0 3px 3px 0; border-radius: 0 0 12px 0; }
.scanner-actions { display: flex; gap: 8px; }
.result-card { border-radius: 14px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.03); padding: 12px; }
.result-card h3 { margin: 0; }
.result-card p { margin: 6px 0 0; color: rgba(255,255,255,.72); }
.result-card--success { border-color: rgba(82,213,139,.55); background: rgba(24,58,45,.35); box-shadow: 0 0 20px rgba(82,213,139,.15); }
.result-card--warning { border-color: rgba(240,190,100,.42); background: rgba(76,56,30,.25); }
.result-card--error { border-color: rgba(255,120,120,.45); background: rgba(80,30,30,.25); }
.checkmark { width: 34px; height: 34px; border-radius: 999px; display: grid; place-items: center; background: rgba(82,213,139,.25); color: #52d58b; font-weight: 700; }
.timestamp { font-size: 12px; color: rgba(255,255,255,.58); }
.manual-grid { margin-top: 10px; display: grid; gap: 10px; }
.muted { color: rgba(255,255,255,.66); }
.permission-note { margin-top: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 10px; }
.permission-note p { margin: 0; font-size: 13px; color: rgba(255,255,255,.72); }
.history-head { display: flex; justify-content: space-between; align-items: center; }
.history-head h2 { margin: 0; }
.history-head span { border-radius: 999px; border: 1px solid rgba(255,255,255,.16); padding: 6px 10px; font-size: 12px; color: rgba(255,255,255,.75); }
.history-list { margin-top: 10px; display: grid; gap: 8px; }
.history-item { display: grid; grid-template-columns: auto 1fr auto; align-items: center; gap: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,.08); background: rgba(255,255,255,.02); padding: 10px; }
.avatar { width: 38px; height: 38px; border-radius: 999px; display: grid; place-items: center; background: linear-gradient(145deg, rgba(244,201,125,.3), rgba(77,57,31,.42)); border: 1px solid rgba(240,190,100,.34); color: #f4d8a7; font-size: 12px; font-weight: 700; }
.name { margin: 0; font-weight: 600; }
.event { margin: 2px 0 0; color: rgba(255,255,255,.62); font-size: 13px; }
.meta { text-align: right; }
.meta p { margin: 5px 0 0; color: rgba(255,255,255,.56); font-size: 12px; }
.chip { border-radius: 999px; border: 1px solid rgba(255,255,255,.15); padding: 4px 9px; font-size: 10px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.82); }
.chip--success { border-color: rgba(82,213,139,.5); color: #52d58b; }
.chip--already_redeemed { border-color: rgba(240,190,100,.48); color: #f4d8a7; }
.chip--expired, .chip--invalid { border-color: rgba(255,120,120,.52); color: #ffaeae; }
.toast { position: fixed; right: 18px; bottom: 18px; z-index: 40; border-radius: 12px; border: 1px solid rgba(240,190,100,.32); background: rgba(10,16,29,.92); color: #f4d8a7; padding: 10px 12px; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 180ms ease, transform 180ms ease; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(8px); }

@keyframes scan {
  0% { top: 8px; }
  50% { top: calc(100% - 10px); }
  100% { top: 8px; }
}

@media (max-width: 1080px) {
  .redemptions__grid {
    grid-template-columns: 1fr;
    grid-template-areas:
      "scanner"
      "manual"
      "history";
  }
}

@media (max-width: 767px) {
  .redemptions { padding: 12px; }
  .redemptions__head { flex-direction: column; }
  .scanner-actions { flex-direction: column; }
  .camera-placeholder { height: 280px; }
  .camera-overlay { width: 190px; height: 190px; }
  .history-item { grid-template-columns: auto 1fr; }
  .meta { grid-column: 2; text-align: left; }
}
</style>
