<template>
  <div class="operator-shell">
    <header class="operator-head">
      <p class="brand">OpenMat Operator</p>
      <button class="legacy-btn" type="button" @click="toolsOpen = true">Tools</button>
    </header>

    <main class="operator-main">
      <RouterView />
    </main>

    <nav class="operator-nav" aria-label="Operator navigation">
      <RouterLink class="tab" :class="{ 'is-active': route.name === 'operator-share' }" to="/operator/share">Share</RouterLink>
      <RouterLink class="tab" :class="{ 'is-active': route.name === 'operator-wallet' }" to="/operator/wallet">Wallet</RouterLink>
    </nav>

    <div class="tools-overlay" :class="{ 'is-open': toolsOpen }" @click="toolsOpen = false"></div>
    <aside class="tools-drawer" :class="{ 'is-open': toolsOpen }" aria-label="Advanced tools">
      <div class="tools-head">
        <p>Advanced Tools</p>
        <button class="close-btn" type="button" @click="toolsOpen = false">Close</button>
      </div>
      <nav class="tools-nav">
        <RouterLink class="tool-link" to="/dashboard/bookings" @click="toolsOpen = false">Bookings</RouterLink>
        <RouterLink class="tool-link" to="/dashboard/payouts" @click="toolsOpen = false">Payouts</RouterLink>
        <RouterLink class="tool-link" to="/dashboard/settings" @click="toolsOpen = false">Settings</RouterLink>
        <RouterLink class="tool-link" to="/dashboard/redemptions" @click="toolsOpen = false">Redemption Scanner</RouterLink>
        <RouterLink class="tool-link" to="/admin/overview" @click="toolsOpen = false">Admin Overview</RouterLink>
        <button class="tool-link" type="button" @click="goLegacy">Legacy dashboard</button>
      </nav>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";

const route = useRoute();
const router = useRouter();
const toolsOpen = ref(false);

function goLegacy() {
  void router.push({ name: "dashboard" });
  toolsOpen.value = false;
}
</script>

<style scoped>
.operator-shell {
  --mvp-gap: 14px;
  --mvp-card-pad: 16px;
  --mvp-radius: 16px;
  --mvp-btn-h: 44px;
  min-height: 100dvh;
  background: radial-gradient(900px 420px at 15% -10%, rgba(38, 91, 169, 0.18), transparent 60%), linear-gradient(180deg, #081a32, #030b18);
  color: #e8eef8;
  padding-bottom: calc(70px + env(safe-area-inset-bottom, 0px));
}
.tools-overlay {
  position: fixed;
  inset: 0;
  z-index: 29;
  background: rgba(4, 10, 20, 0.54);
  opacity: 0;
  pointer-events: none;
  transition: opacity 160ms ease;
}
.tools-overlay.is-open { opacity: 1; pointer-events: auto; }
.tools-drawer {
  position: fixed;
  right: 0;
  top: 0;
  bottom: 0;
  width: min(90vw, 340px);
  z-index: 30;
  transform: translateX(100%);
  transition: transform 180ms ease;
  border-left: 1px solid rgba(255,255,255,.14);
  background: rgba(8, 16, 30, 0.96);
  backdrop-filter: blur(12px);
  padding: 14px;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 12px;
}
.tools-drawer.is-open { transform: translateX(0); }
.tools-head { display: flex; align-items: center; justify-content: space-between; }
.tools-head p { margin: 0; font-weight: 650; color: #f4d8a7; }
.close-btn { min-height: 38px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.05); color: #dbe5f3; padding: 0 10px; }
.tools-nav { display: grid; align-content: start; gap: 8px; }
.tool-link {
  min-height: 44px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(255,255,255,.04);
  color: rgba(233,241,252,.86);
  text-decoration: none;
  display: flex;
  align-items: center;
  padding: 0 12px;
  font-size: 14px;
}
.operator-head {
  position: sticky;
  top: 0;
  z-index: 12;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(5, 12, 24, 0.8);
  backdrop-filter: blur(14px);
}
.brand { margin: 0; font-size: 14px; letter-spacing: .08em; text-transform: uppercase; color: #f4d8a7; }
.legacy-btn {
  min-height: 40px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,.18);
  background: rgba(255,255,255,.05);
  color: #dbe5f3;
  padding: 0 12px;
}
.operator-main { padding: 14px 12px 0; }
.operator-nav {
  position: fixed;
  left: 10px;
  right: 10px;
  bottom: calc(10px + env(safe-area-inset-bottom, 0px));
  z-index: 20;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 8px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.12);
  background: rgba(8, 16, 30, 0.9);
  backdrop-filter: blur(10px);
}
.tab {
  min-height: 44px;
  border-radius: 10px;
  display: grid;
  place-items: center;
  color: rgba(233, 241, 252, 0.72);
  text-decoration: none;
  font-weight: 600;
}
.tab.is-active {
  background: linear-gradient(145deg, #f3d89f, #e9c57b);
  color: #0c1728;
}
@media (min-width: 1024px) {
  .operator-shell { max-width: 720px; margin: 0 auto; border-inline: 1px solid rgba(255,255,255,.08); }
}
</style>
