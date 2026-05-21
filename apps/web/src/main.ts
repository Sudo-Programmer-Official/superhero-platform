import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { hasFirebaseConfig } from "./firebase/config";
import "./style.css";
import "./shared/styles/foundation.css";

if (!hasFirebaseConfig) {
  console.warn("[web] Firebase config is incomplete. Fill VITE_FIREBASE_* env vars.");
}

if ("serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch((err) => {
      console.warn("[web] service worker registration failed", err);
    });
  });
}

createApp(App).use(router).mount("#app");
