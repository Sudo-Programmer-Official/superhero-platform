<template>
  <section v-if="isAuthResolving" class="app-auth-loading" aria-live="polite" aria-busy="true">
    <div class="app-auth-loading__card">
      <p class="app-auth-loading__brand">OpenMat App</p>
      <div class="app-auth-loading__pulse"></div>
      <p class="app-auth-loading__copy">Verifying session…</p>
    </div>
  </section>

  <div v-else class="app-shell">
    <header class="app-head">
      <p class="brand">OpenMat</p>
      <button class="advanced-btn" type="button" @click="drawerOpen = true">Advanced</button>
    </header>

    <main class="app-main">
      <RouterView />
    </main>

    <nav class="dock" aria-label="Primary app navigation">
      <RouterLink class="dock-item" :class="{ active: isActive('app-deals') }" to="/app/deals">
        <i class="icon" aria-hidden="true"><IconTicket /></i>
        <span>Deals</span>
      </RouterLink>
      <RouterLink class="dock-item dock-item--create" :class="{ active: isActive('app-deals-create') }" to="/app/deals/create">
        <i class="icon" aria-hidden="true"><IconPlus /></i>
        <span>Create</span>
      </RouterLink>
      <RouterLink class="dock-item" :class="{ active: isActive('app-redemptions') }" to="/app/redemptions">
        <i class="icon" aria-hidden="true"><IconScan /></i>
        <span>Redemptions</span>
      </RouterLink>
      <RouterLink class="dock-item" :class="{ active: isActive('app-payouts') }" to="/app/payouts">
        <i class="icon" aria-hidden="true"><IconDollar /></i>
        <span>Payouts</span>
      </RouterLink>
      <RouterLink class="dock-item" :class="{ active: isActive('app-profile') }" to="/app/profile">
        <i class="icon" aria-hidden="true"><IconUser /></i>
        <span>Profile</span>
      </RouterLink>
    </nav>

    <div class="overlay" :class="{ open: drawerOpen }" @click="drawerOpen = false"></div>
    <aside class="drawer" :class="{ open: drawerOpen }" aria-label="Workspace tools">
      <div class="drawer-head">
        <p>Advanced Tools</p>
        <button class="close-btn" type="button" @click="drawerOpen = false">Close</button>
      </div>
      <nav class="drawer-nav">
        <RouterLink class="tool-link" to="/dashboard" @click="drawerOpen = false">Legacy dashboard</RouterLink>
        <RouterLink class="tool-link" to="/dashboard/bookings" @click="drawerOpen = false">Bookings</RouterLink>
        <RouterLink class="tool-link" to="/dashboard/wallet-passes" @click="drawerOpen = false">Wallet passes</RouterLink>
        <RouterLink class="tool-link" to="/dashboard/settings" @click="drawerOpen = false">Settings</RouterLink>
        <RouterLink class="tool-link" to="/admin/overview" @click="drawerOpen = false">Admin</RouterLink>
      </nav>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, ref } from "vue";
import { useRoute } from "vue-router";
import { sessionState } from "../stores/session";

const route = useRoute();
const drawerOpen = ref(false);
const isAuthResolving = computed(() => sessionState.authState === "loading" || (sessionState.token && !sessionState.meLoaded));

function isActive(name: string): boolean {
  return String(route.name || "") === name;
}

const IconBase = defineComponent({
  props: { path: { type: String, required: true } },
  setup(props) {
    return () =>
      h("svg", { viewBox: "0 0 24 24", fill: "none", stroke: "currentColor", "stroke-width": "1.8", "stroke-linecap": "round", "stroke-linejoin": "round" }, [
        h("path", { d: props.path })
      ]);
  }
});
const IconTicket = () => h(IconBase, { path: "M3 9a3 3 0 0 0 0 6v4h18v-4a3 3 0 0 0 0-6V5H3z M12 5v14" });
const IconScan = () => h(IconBase, { path: "M4 7V5h2 M20 7V5h-2 M4 17v2h2 M20 17v2h-2 M7 12h10" });
const IconDollar = () => h(IconBase, { path: "M12 3v18 M16 7c0-1.7-1.8-3-4-3s-4 1.3-4 3 1.8 3 4 3 4 1.3 4 3-1.8 3-4 3-4-1.3-4-3" });
const IconUser = () => h(IconBase, { path: "M20 21a8 8 0 0 0-16 0 M12 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8" });
const IconPlus = () => h(IconBase, { path: "M12 5v14 M5 12h14" });
</script>

<style scoped>
.app-shell { min-height: 100dvh; background: radial-gradient(900px 420px at 15% -10%, rgba(38, 91, 169, 0.18), transparent 60%), linear-gradient(180deg, #081a32, #030b18); color: #e8eef8; padding-bottom: calc(116px + env(safe-area-inset-bottom, 0px)); }
.app-head { position: sticky; top: 0; z-index: 20; min-height: 62px; display: flex; align-items: center; justify-content: space-between; padding: 10px 14px; border-bottom: 1px solid rgba(255,255,255,.1); background: rgba(5, 12, 24, .76); backdrop-filter: blur(12px); }
.brand { margin: 0; font-weight: 700; letter-spacing: -.02em; font-size: 20px; }
.advanced-btn { min-height: 40px; border-radius: 12px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.05); color: #dbe5f3; padding: 0 12px; }
.app-main { padding: 12px; max-width: 760px; margin: 0 auto; }
.dock { position: fixed; left: 12px; right: 12px; bottom: calc(10px + env(safe-area-inset-bottom, 0px)); z-index: 25; border-radius: 18px; border: 1px solid rgba(255,255,255,.14); background: rgba(7,14,24,.92); backdrop-filter: blur(12px); padding: 8px; display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 6px; }
.dock-item { min-height: 54px; border-radius: 12px; text-decoration: none; color: rgba(233, 241, 252, 0.68); display: grid; justify-items: center; align-content: center; gap: 3px; border: 1px solid transparent; transition: all .18s ease; }
.dock-item .icon { width: 20px; height: 20px; display: grid; }
.dock-item .icon :deep(svg) { width: 20px; height: 20px; }
.dock-item span { font-size: 10px; font-weight: 600; opacity: 0; transform: translateY(2px); max-height: 0; overflow: hidden; transition: opacity .16s ease, transform .16s ease, max-height .16s ease; }
.dock-item--create {
  color: #0c1728;
  border-color: rgba(240,190,100,.45);
  background: linear-gradient(145deg, #f3d89f, #e9c57b);
  box-shadow: 0 10px 24px rgba(0,0,0,.22);
  align-content: center;
  gap: 2px;
}
.dock-item--create .icon {
  color: #0c1728;
  margin-top: 0;
}
.dock-item--create span {
  color: #0c1728;
  opacity: 1;
  transform: translateY(0);
  max-height: 18px;
  line-height: 1;
}
.dock-item.active { color: #f4d8a7; border-color: rgba(240,190,100,.38); background: rgba(240,190,100,.12); box-shadow: inset 0 0 0 1px rgba(240,190,100,.14); }
.dock-item.active span { opacity: 1; transform: translateY(0); max-height: 18px; }
.dock-item:not(.active) { color: rgba(233, 241, 252, 0.56); }
.dock-item:hover { color: rgba(244, 216, 167, 0.9); }
.overlay { position: fixed; inset: 0; z-index: 29; background: rgba(4,10,20,.56); opacity: 0; pointer-events: none; transition: opacity .16s ease; }
.overlay.open { opacity: 1; pointer-events: auto; }
.drawer { position: fixed; right: 0; top: 0; bottom: 0; width: min(90vw, 340px); z-index: 30; transform: translateX(100%); transition: transform .18s ease; border-left: 1px solid rgba(255,255,255,.14); background: rgba(8,16,30,.96); backdrop-filter: blur(12px); padding: 14px; display: grid; grid-template-rows: auto 1fr; gap: 10px; }
.drawer.open { transform: translateX(0); }
.drawer-head { display: flex; align-items: center; justify-content: space-between; }
.drawer-head p { margin: 0; color: #f4d8a7; font-weight: 650; }
.close-btn { min-height: 38px; border-radius: 10px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.05); color: #dbe5f3; padding: 0 10px; }
.drawer-nav { display: grid; align-content: start; gap: 8px; }
.tool-link { min-height: 44px; border-radius: 10px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.04); color: rgba(233,241,252,.86); text-decoration: none; display: flex; align-items: center; padding: 0 12px; }
.app-auth-loading { min-height: 100dvh; display: grid; place-items: center; padding: 24px; background: radial-gradient(900px 420px at 15% -10%, rgba(38, 91, 169, 0.18), transparent 60%), linear-gradient(180deg, #081a32, #030b18); color: #e8eef8; }
.app-auth-loading__card { width: min(92vw, 420px); border: 1px solid rgba(255,255,255,.12); border-radius: 16px; background: rgba(8, 16, 30, 0.88); padding: 18px; display: grid; gap: 12px; }
.app-auth-loading__brand { margin: 0; color: #f4d8a7; text-transform: uppercase; letter-spacing: .08em; font-size: 12px; }
.app-auth-loading__copy { margin: 0; color: rgba(233,241,252,.76); font-size: 14px; }
.app-auth-loading__pulse { height: 10px; border-radius: 999px; background: linear-gradient(90deg, rgba(113,182,255,.18), rgba(113,182,255,.5), rgba(113,182,255,.18)); background-size: 200% 100%; animation: pulse 1.2s linear infinite; }
@keyframes pulse { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
@media (min-width: 1024px) { .app-shell { max-width: 760px; margin: 0 auto; border-inline: 1px solid rgba(255,255,255,.08);} }
@media (min-width: 720px) {
  .dock-item span { opacity: .86; transform: translateY(0); max-height: 18px; }
}
</style>
