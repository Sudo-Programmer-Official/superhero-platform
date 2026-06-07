import { createApp } from "vue";
import { registerSW } from "virtual:pwa-register";
import App from "./App.vue";
import router from "./router";
import { hasFirebaseConfig } from "./firebase/config";
import { setAuthFailureHandler } from "./services/api";
import { clearSessionState } from "./stores/session";
import "./design-system/index.css";
import "./style.css";

if (!hasFirebaseConfig) {
  console.warn("[web] Firebase config is incomplete. Fill VITE_FIREBASE_* env vars.");
}

registerSW({ immediate: true });

setAuthFailureHandler(() => {
  clearSessionState();
  try {
    window.localStorage.removeItem("openmat:last-checkout-success");
  } catch {
    // Ignore storage availability errors.
  }
  const next = encodeURIComponent(`${window.location.pathname}${window.location.search}`);
  if (!window.location.pathname.startsWith("/sign-in")) {
    window.location.assign(`/sign-in?next=${next}`);
  }
});

createApp(App).use(router).mount("#app");
