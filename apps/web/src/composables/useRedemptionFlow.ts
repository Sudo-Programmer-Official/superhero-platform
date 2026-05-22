import { computed, ref } from "vue";
import { redeemWalletPass } from "../services/api";
import { sessionState } from "../stores/session";

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

export function useRedemptionFlow() {
  const scannerState = ref<ScannerState>("idle");
  const cameraPermission = ref<PermissionState>("not_requested");
  const manualCode = ref("");
  const toast = ref("");
  const result = ref<RedemptionResult | null>(null);
  const history = ref<RedemptionHistoryItem[]>([]);
  const isSubmitting = computed(() => scannerState.value === "validating");
  const canUseNativeDetector = ref(false);
  const videoEl = ref<HTMLVideoElement | null>(null);
  const cameraStream = ref<MediaStream | null>(null);
  const scannerError = ref("");
  let scanRafId: number | null = null;

  const canSubmitManual = computed(() => manualCode.value.trim().length > 0 && !isSubmitting.value);

  const stateLabel = computed(() => scannerState.value.replace(/_/g, " "));

  function setToast(message: string) {
    toast.value = message;
    window.setTimeout(() => {
      if (toast.value === message) {
        toast.value = "";
      }
    }, 2200);
  }

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
      setToast("Camera denied. Use manual fallback.");
    }
  }

  function reset() {
    teardownScanner();
    scannerState.value = "idle";
    manualCode.value = "";
    result.value = null;
  }

  async function redeemCode(inputCode: string) {
    const code = inputCode.trim();
    if (!code) return;
    if (!sessionState.token) {
      scannerState.value = "offline";
      setToast("Authentication session expired.");
      pushHistory(code, "invalid");
      return;
    }

    scannerState.value = "validating";
    teardownScanner();
    await wait(450);

    try {
      await redeemWalletPass(sessionState.token, code);
      const attendeeName = pickFrom(code, MOCK_NAMES);
      const eventName = pickFrom(`${code}:event`, MOCK_EVENTS);
      result.value = {
        attendeeName,
        eventName,
        redeemedAt: new Date().toISOString(),
        code
      };
      scannerState.value = "success";
      setToast("Pass redeemed successfully.");
      pushHistory(code, "success");
    } catch (err) {
      const message = String(err).toLowerCase();
      if (message.includes("409") && message.includes("already")) {
        scannerState.value = "already_redeemed";
        pushHistory(code, "already_redeemed");
        return;
      }
      if (message.includes("409") && message.includes("expired")) {
        scannerState.value = "expired";
        pushHistory(code, "expired");
        return;
      }
      if (message.includes("404") || message.includes("failed redeem")) {
        scannerState.value = "invalid";
        pushHistory(code, "invalid");
        return;
      }
      if (message.includes("network") || message.includes("offline")) {
        scannerState.value = "offline";
        pushHistory(code, "invalid");
        return;
      }
      scannerState.value = "invalid";
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
    setVideoElement,
    setToast,
    simulateScan,
    stateLabel,
    teardownScanner,
    toast
  };
}
