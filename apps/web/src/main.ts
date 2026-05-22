import { createApp } from "vue";
import App from "./App.vue";
import router from "./router";
import { hasFirebaseConfig } from "./firebase/config";
import "./design-system/index.css";
import "./style.css";

if (!hasFirebaseConfig) {
  console.warn("[web] Firebase config is incomplete. Fill VITE_FIREBASE_* env vars.");
}

if (import.meta.env.PROD && "serviceWorker" in navigator) {
  window.addEventListener("load", () => {
    navigator.serviceWorker.register("/sw.js").catch((err) => {
      console.warn("[web] service worker registration failed", err);
    });
  });
}

createApp(App).use(router).mount("#app");
