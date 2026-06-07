import { computed, onMounted, ref } from "vue";

type BeforeInstallPromptEvent = Event & {
  prompt: () => Promise<void>;
  userChoice: Promise<{ outcome: "accepted" | "dismissed"; platform: string }>;
};

const STORAGE_DISMISS_KEY = "openmat:pwa-install-dismissed";
const STORAGE_INSTALLED_KEY = "openmat:pwa-installed";

const deferredPrompt = ref<BeforeInstallPromptEvent | null>(null);
const installDismissed = ref(false);
const standaloneInstalled = ref(false);
const isIOS = ref(false);
const isSafari = ref(false);

export function usePWAInstall() {
  const isInstallable = computed(() => Boolean(deferredPrompt.value) && !installDismissed.value && !standaloneInstalled.value);
  const isInstalled = computed(() => standaloneInstalled.value);
  const showIOSInstructions = computed(() => isIOS.value && isSafari.value && !standaloneInstalled.value && !installDismissed.value);

  function dismissInstallPrompt() {
    installDismissed.value = true;
    try {
      window.localStorage.setItem(STORAGE_DISMISS_KEY, "1");
    } catch {
      // ignore storage errors
    }
  }

  async function install() {
    if (deferredPrompt.value) {
      await deferredPrompt.value.prompt();
      const choice = await deferredPrompt.value.userChoice;
      if (choice.outcome === "accepted") {
        deferredPrompt.value = null;
        standaloneInstalled.value = true;
        try {
          window.localStorage.setItem(STORAGE_INSTALLED_KEY, "1");
        } catch {
          // ignore storage errors
        }
        return;
      }
      dismissInstallPrompt();
      return;
    }
  }

  onMounted(() => {
    const ua = navigator.userAgent || "";
    isIOS.value = /iPad|iPhone|iPod/.test(ua);
    isSafari.value = /^((?!chrome|android).)*safari/i.test(ua);
    standaloneInstalled.value =
      window.matchMedia?.("(display-mode: standalone)")?.matches ||
      (window.navigator as Navigator & { standalone?: boolean }).standalone === true;

    try {
      installDismissed.value = window.localStorage.getItem(STORAGE_DISMISS_KEY) === "1";
      standaloneInstalled.value = standaloneInstalled.value || window.localStorage.getItem(STORAGE_INSTALLED_KEY) === "1";
    } catch {
      // ignore storage errors
    }

    window.addEventListener("beforeinstallprompt", (event) => {
      event.preventDefault();
      deferredPrompt.value = event as BeforeInstallPromptEvent;
    });

    window.addEventListener("appinstalled", () => {
      standaloneInstalled.value = true;
      deferredPrompt.value = null;
      try {
        window.localStorage.setItem(STORAGE_INSTALLED_KEY, "1");
      } catch {
        // ignore storage errors
      }
    });
  });

  return {
    install,
    dismissInstallPrompt,
    isInstallable,
    isInstalled,
    showIOSInstructions
  };
}
