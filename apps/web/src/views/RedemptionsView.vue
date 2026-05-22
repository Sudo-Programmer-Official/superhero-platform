<template>
  <section class="redemptions">
    <header class="redemptions__head">
      <div>
        <p class="eyebrow">Redemption Flow</p>
        <h1>Scan and Redeem</h1>
        <p>Camera-first QR redemption with manual fallback.</p>
      </div>
      <span class="state-pill" :class="`is-${scannerState}`">{{ scannerState.replace('_', ' ') }}</span>
    </header>

    <div class="redemptions__grid">
      <AppCard class="scanner-card">
        <h2>Scanner</h2>

        <div v-if="scannerState === 'idle'" class="scanner-state">
          <p>Ready to scan a wallet pass QR code.</p>
          <AppButton variant="primary" size="form" @click="onStartScan">Scan pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'requesting_camera'" class="scanner-state">
          <p>Requesting camera access…</p>
        </div>

        <div v-else-if="scannerState === 'scanning'" class="scanner-state">
          <div class="camera-placeholder">
            <div class="scan-frame"></div>
            <p>Camera live preview placeholder</p>
          </div>
          <div class="scanner-actions">
            <AppButton variant="secondary" size="form" @click="simulateDetectedCode">Simulate QR detect</AppButton>
            <AppButton variant="ghost" size="form" @click="onCancelScan">Cancel</AppButton>
          </div>
        </div>

        <div v-else-if="scannerState === 'validating'" class="scanner-state">
          <p>Validating pass…</p>
        </div>

        <div v-else-if="scannerState === 'success'" class="scanner-state state-success">
          <p>Pass redeemed successfully.</p>
          <AppButton variant="primary" size="form" @click="resetState">Scan next pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'already_redeemed'" class="scanner-state state-warning">
          <p>This pass has already been redeemed.</p>
          <AppButton variant="secondary" size="form" @click="resetState">Try another pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'expired'" class="scanner-state state-error">
          <p>This pass is expired and cannot be redeemed.</p>
          <AppButton variant="secondary" size="form" @click="resetState">Try another pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'invalid'" class="scanner-state state-error">
          <p>Invalid pass code.</p>
          <AppButton variant="secondary" size="form" @click="resetState">Try another pass</AppButton>
        </div>

        <div v-else-if="scannerState === 'offline'" class="scanner-state state-warning">
          <p>Network unavailable. Check your connection.</p>
          <AppButton variant="secondary" size="form" @click="resetState">Retry</AppButton>
        </div>
      </AppCard>

      <AppCard>
        <h2>Manual fallback</h2>
        <p class="muted">If camera access is denied, enter QR code manually.</p>
        <div class="manual-grid">
          <AppInput v-model="manualCode" placeholder="Enter redemption code" />
          <AppButton
            variant="primary"
            size="form"
            :disabled="!manualCode.trim() || scannerState === 'validating'"
            @click="onManualRedeem"
          >
            Redeem manually
          </AppButton>
        </div>

        <div class="permission-note">
          <p><strong>Camera permission:</strong> {{ cameraPermission }}</p>
        </div>
      </AppCard>
    </div>

    <transition name="toast-fade">
      <div v-if="toast" class="toast">{{ toast }}</div>
    </transition>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import AppInput from "../design-system/primitives/AppInput.vue";
import { redeemWalletPass } from "../services/api";
import { sessionState } from "../stores/session";

type ScannerState =
  | "idle"
  | "requesting_camera"
  | "scanning"
  | "validating"
  | "success"
  | "invalid"
  | "already_redeemed"
  | "expired"
  | "offline";

const scannerState = ref<ScannerState>("idle");
const manualCode = ref("");
const cameraPermission = ref("not_requested");
const toast = ref("");

function setToast(message: string) {
  toast.value = message;
  setTimeout(() => {
    if (toast.value === message) toast.value = "";
  }, 2200);
}

function resetState() {
  scannerState.value = "idle";
  manualCode.value = "";
}

async function onStartScan() {
  scannerState.value = "requesting_camera";

  try {
    await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
    cameraPermission.value = "granted";
    scannerState.value = "scanning";
  } catch {
    cameraPermission.value = "denied";
    scannerState.value = "idle";
    setToast("Camera denied. Use manual code fallback.");
  }
}

function onCancelScan() {
  resetState();
}

function simulateDetectedCode() {
  // Simulate detector output and move into validation.
  manualCode.value = "SIMULATED_QR_CODE";
  void runRedeem(manualCode.value);
}

async function onManualRedeem() {
  await runRedeem(manualCode.value);
}

async function runRedeem(code: string) {
  if (!sessionState.token) {
    scannerState.value = "offline";
    setToast("Authentication session expired.");
    return;
  }

  scannerState.value = "validating";
  try {
    await redeemWalletPass(sessionState.token, code.trim());
    scannerState.value = "success";
    setToast("Pass redeemed successfully.");
  } catch (err) {
    const message = String(err).toLowerCase();
    if (message.includes("409") && message.includes("already")) {
      scannerState.value = "already_redeemed";
      return;
    }
    if (message.includes("409") && message.includes("expired")) {
      scannerState.value = "expired";
      return;
    }
    if (message.includes("failed redeem: 404")) {
      scannerState.value = "invalid";
      return;
    }
    if (message.includes("network") || message.includes("offline")) {
      scannerState.value = "offline";
      return;
    }
    scannerState.value = "invalid";
  }
}
</script>

<style scoped>
.redemptions { padding: 18px; display: grid; gap: 12px; }
.redemptions__head { display: flex; align-items: flex-start; justify-content: space-between; gap: 12px; }
.redemptions__head h1 { margin: 6px 0 0; font-size: clamp(30px, 4vw, 46px); }
.redemptions__head p { margin: 8px 0 0; color: rgba(255,255,255,.66); }
.state-pill { border-radius: 999px; border: 1px solid rgba(255,255,255,.2); padding: 7px 12px; text-transform: uppercase; letter-spacing: .08em; font-size: 11px; color: rgba(255,255,255,.82); }
.state-pill.is-success { border-color: rgba(82,213,139,.55); color: #52d58b; }
.state-pill.is-invalid, .state-pill.is-expired { border-color: rgba(255,120,120,.6); color: #ff9a9a; }
.state-pill.is-already_redeemed, .state-pill.is-offline { border-color: rgba(240,190,100,.5); color: #f4d8a7; }
.redemptions__grid { display: grid; grid-template-columns: 1fr 420px; gap: 12px; }
.scanner-state { display: grid; gap: 10px; margin-top: 8px; }
.camera-placeholder { height: 300px; border-radius: 16px; border: 1px dashed rgba(255,255,255,.24); background: rgba(9,15,26,.76); display: grid; place-items: center; color: rgba(255,255,255,.62); }
.scan-frame { width: 170px; height: 170px; border: 2px solid rgba(240,190,100,.7); border-radius: 16px; box-shadow: 0 0 0 1px rgba(240,190,100,.15), 0 0 24px rgba(240,190,100,.15); margin-bottom: 10px; }
.scanner-actions { display: flex; gap: 8px; }
.state-success p { color: #52d58b; }
.state-warning p { color: #f4d8a7; }
.state-error p { color: #ff9a9a; }
.manual-grid { margin-top: 10px; display: grid; gap: 10px; }
.muted { color: rgba(255,255,255,.66); }
.permission-note { margin-top: 10px; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 10px; }
.permission-note p { margin: 0; font-size: 13px; color: rgba(255,255,255,.72); }
.toast { position: fixed; right: 18px; bottom: 18px; z-index: 40; border-radius: 12px; border: 1px solid rgba(240,190,100,.32); background: rgba(10,16,29,.92); color: #f4d8a7; padding: 10px 12px; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 180ms ease, transform 180ms ease; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(8px); }
@media (max-width: 1080px) { .redemptions__grid { grid-template-columns: 1fr; } }
@media (max-width: 767px) {
  .redemptions { padding: 12px; }
  .redemptions__head { flex-direction: column; }
  .scanner-actions { flex-direction: column; }
  .camera-placeholder { height: 240px; }
}
</style>
