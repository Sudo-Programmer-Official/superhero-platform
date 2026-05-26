import { computed, ref } from "vue";
import { ApiHttpError, redeemWalletPass } from "../services/api";
import { sessionState } from "../stores/session";
import { showToast } from "../stores/toast";

export type ScannerState =
  | "idle"
  | "requesting_camera"
  | "scanning"
  | "validating"
  | "success"
  | "invalid"
  | "already_redeemed"
  | "expired"
  | "offline";

type PermissionState = "not_requested" | "granted" | "denied";

type RedemptionResult = {
  attendeeName: string;
  eventName: string;
  redeemedAt: string;
  code: string;
  operatorLabel: string;
  deviceLabel: string;
};

export type RedemptionHistoryItem = {
  id: string;
  attendeeName: string;
  eventName: string;
  timestamp: string;
  avatarInitials: string;
  status: "success" | "already_redeemed" | "invalid" | "expired";
};

const MOCK_NAMES = ["Ava Reed", "Megan Cruz", "Jess Kim", "Noah Bell", "Mila Gray", "Eli Park"];
const MOCK_EVENTS = ["Breathwork Journey", "Morning Flow Yoga", "Sound Bath Evening", "Mobility Reset"];

function pickFrom(input: string, values: string[]): string {
  const seed = input
    .split("")
    .reduce((sum, char) => sum + char.charCodeAt(0), 0);
  return values[seed % values.length];
}

function initials(name: string): string {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("") || "NA";
}

function wait(ms: number): Promise<void> {
  return new Promise((resolve) => {
    window.setTimeout(resolve, ms);
  });
}

function triggerHaptic(kind: "success" | "warning" | "error") {
  if (typeof navigator === "undefined" || typeof navigator.vibrate !== "function") return;
  if (kind === "success") navigator.vibrate([20, 30, 20]);
  if (kind === "warning") navigator.vibrate([35, 30, 35]);
  if (kind === "error") navigator.vibrate([60, 40, 60]);
}

export function useRedemptionFlow() {
  const scannerState = ref<ScannerState>("idle");
  const cameraPermission = ref<PermissionState>("not_requested");
  const manualCode = ref("");
  const result = ref<RedemptionResult | null>(null);
  const history = ref<RedemptionHistoryItem[]>([]);
  const isSubmitting = computed(() => scannerState.value === "validating");
  const canUseNativeDetector = ref(false);
  const videoEl = ref<HTMLVideoElement | null>(null);
  const cameraStream = ref<MediaStream | null>(null);
  const scannerError = ref("");
  const statusNote = ref("");
  let scanRafId: number | null = null;

  const canSubmitManual = computed(() => manualCode.value.trim().length > 0 && !isSubmitting.value);

  const stateLabel = computed(() => scannerState.value.replace(/_/g, " "));

  function stopScanLoop() {
    if (scanRafId) {
      window.cancelAnimationFrame(scanRafId);
      scanRafId = null;
    }
  }

  function teardownScanner() {
    stopScanLoop();
    if (cameraStream.value) {
      cameraStream.value.getTracks().forEach((track) => track.stop());
      cameraStream.value = null;
    }
    if (videoEl.value) {
      videoEl.value.pause();
      videoEl.value.srcObject = null;
    }
  }

  function setVideoElement(el: HTMLVideoElement | null) {
    videoEl.value = el;
  }

  async function bootNativeScanner() {
    const detectorCtor = (window as Window & { BarcodeDetector?: new (opts?: { formats?: string[] }) => { detect: (input: ImageBitmapSource) => Promise<Array<{ rawValue?: string }>> } }).BarcodeDetector;
    if (!detectorCtor || !videoEl.value || !cameraStream.value) {
      canUseNativeDetector.value = false;
      return;
    }
    canUseNativeDetector.value = true;
    const detector = new detectorCtor({ formats: ["qr_code"] });
    const tick = async () => {
      if (scannerState.value !== "scanning" || !videoEl.value) return;
      try {
        const barcodes = await detector.detect(videoEl.value);
        const value = barcodes[0]?.rawValue?.trim();
        if (value) {
          manualCode.value = value;
          teardownScanner();
          await redeemCode(value);
          return;
        }
      } catch {
        scannerError.value = "Live decode failed. Use manual fallback.";
      }
      scanRafId = window.requestAnimationFrame(() => {
        void tick();
      });
    };
    scanRafId = window.requestAnimationFrame(() => {
      void tick();
    });
  }

  function pushHistory(code: string, status: RedemptionHistoryItem["status"]) {
    const attendeeName = pickFrom(code, MOCK_NAMES);
    const eventName = pickFrom(`${code}:event`, MOCK_EVENTS);
    history.value.unshift({
      id: `${Date.now()}-${code.slice(0, 10)}`,
      attendeeName,
      eventName,
      timestamp: new Date().toISOString(),
      avatarInitials: initials(attendeeName),
      status
    });
    history.value = history.value.slice(0, 8);
  }

  function hydrateMockHistory() {
    if (history.value.length > 0) return;
    const now = Date.now();
    history.value = [
      {
        id: "h1",
        attendeeName: "Jess Kim",
        eventName: "Breathwork Journey",
        timestamp: new Date(now - 2 * 60 * 1000).toISOString(),
        avatarInitials: "JK",
        status: "success"
      },
      {
        id: "h2",
        attendeeName: "Megan Cruz",
        eventName: "Morning Flow Yoga",
        timestamp: new Date(now - 17 * 60 * 1000).toISOString(),
        avatarInitials: "MC",
        status: "already_redeemed"
      },
      {
        id: "h3",
        attendeeName: "Ava Reed",
        eventName: "Sound Bath Evening",
        timestamp: new Date(now - 46 * 60 * 1000).toISOString(),
        avatarInitials: "AR",
        status: "expired"
      }
    ];
  }

  async function requestCameraAndScan() {
    scannerState.value = "requesting_camera";
    try {
      scannerError.value = "";
      cameraStream.value = await navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } });
      cameraPermission.value = "granted";
      scannerState.value = "scanning";
      if (videoEl.value) {
        videoEl.value.srcObject = cameraStream.value;
        await videoEl.value.play();
      }
      await bootNativeScanner();
    } catch {
      cameraPermission.value = "denied";
      scannerState.value = "idle";
      triggerHaptic("warning");
      showToast("Camera denied. Use manual fallback.", "warning");
    }
  }

  function reset() {
    teardownScanner();
    scannerState.value = "idle";
    manualCode.value = "";
    result.value = null;
    statusNote.value = "";
  }

  async function redeemCode(inputCode: string) {
    const code = inputCode.trim();
    if (!code) return;
    if (!sessionState.token) {
      scannerState.value = "offline";
      triggerHaptic("error");
      showToast("Authentication session expired.", "error");
      pushHistory(code, "invalid");
      return;
    }

    scannerState.value = "validating";
    teardownScanner();
    await wait(450);

    try {
      const payload = await redeemWalletPass(sessionState.token, code);
      const attendeeName = payload.attendee_name || pickFrom(code, MOCK_NAMES);
      const eventName = payload.deal_title || pickFrom(`${code}:event`, MOCK_EVENTS);
      const operatorLabel = sessionState.user?.displayName?.trim() || sessionState.me?.email || "OpenMat Operator";
      const deviceLabel = navigator.userAgent.includes("Mobile") ? "Mobile scanner" : "Web scanner";
      result.value = {
        attendeeName,
        eventName,
        redeemedAt: payload.redeemed_at || new Date().toISOString(),
        code,
        operatorLabel,
        deviceLabel
      };
      statusNote.value = "";
      scannerState.value = "success";
      triggerHaptic("success");
      showToast("Pass redeemed successfully.", "success");
      pushHistory(code, "success");
    } catch (err: unknown) {
      if (err instanceof ApiHttpError && err.status === 409) {
        const detail = (typeof err.detail === "object" && err.detail ? err.detail : {}) as Record<string, unknown>;
        const reason = String(detail.reason || "").toLowerCase();
        if (reason === "already_redeemed") {
          const at = detail.redeemed_at ? new Date(String(detail.redeemed_at)).toLocaleString() : "unknown time";
          statusNote.value = `Previously redeemed at ${at}.`;
          scannerState.value = "already_redeemed";
          triggerHaptic("warning");
          showToast("Already redeemed. No new action required.", "warning");
          pushHistory(code, "already_redeemed");
          return;
        }
        if (reason === "expired") {
          const at = detail.expires_at ? new Date(String(detail.expires_at)).toLocaleString() : "expiry unknown";
          statusNote.value = `Pass expired at ${at}.`;
          scannerState.value = "expired";
          triggerHaptic("warning");
          showToast("Pass is expired.", "warning");
          pushHistory(code, "expired");
          return;
        }
      }

      const message = String(err).toLowerCase();
      if (message.includes("409") && message.includes("already")) {
        scannerState.value = "already_redeemed";
        statusNote.value = "This pass was already redeemed earlier.";
        triggerHaptic("warning");
        pushHistory(code, "already_redeemed");
        return;
      }
      if (message.includes("409") && message.includes("expired")) {
        scannerState.value = "expired";
        statusNote.value = "This pass has expired and cannot be redeemed.";
        triggerHaptic("warning");
        pushHistory(code, "expired");
        return;
      }
      if (message.includes("404") || message.includes("failed redeem")) {
        scannerState.value = "invalid";
        statusNote.value = "Code not found or invalid.";
        triggerHaptic("error");
        showToast("Invalid pass code.", "error");
        pushHistory(code, "invalid");
        return;
      }
      if (message.includes("network") || message.includes("offline")) {
        scannerState.value = "offline";
        statusNote.value = "Network issue detected. Retry when online.";
        triggerHaptic("error");
        pushHistory(code, "invalid");
        return;
      }
      scannerState.value = "invalid";
      statusNote.value = "Pass validation failed.";
      triggerHaptic("error");
      pushHistory(code, "invalid");
    }
  }

  function simulateScan() {
    const code = `OM-${Math.random().toString(36).slice(2, 8).toUpperCase()}`;
    manualCode.value = code;
    void redeemCode(code);
  }

  return {
    canUseNativeDetector,
    cameraPermission,
    canSubmitManual,
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
    statusNote,
    setVideoElement,
    simulateScan,
    stateLabel,
    teardownScanner
  };
}
