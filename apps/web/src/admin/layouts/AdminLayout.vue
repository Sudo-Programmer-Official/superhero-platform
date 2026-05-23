<template>
  <div class="admin-shell">
    <aside class="admin-sidebar">
      <div class="brand">
        <span>OpenMat</span>
        <strong>Control Center</strong>
      </div>
      <nav class="nav">
        <section v-for="group in navGroups" :key="group.section" class="nav-group">
          <p class="nav-group__title">{{ group.section }}</p>
          <RouterLink
            v-for="item in group.items"
            :key="item.id"
            class="nav-item"
            :class="{ 'is-active': route.name === item.route }"
            :to="{ name: item.route }"
          >
            {{ item.label }}
          </RouterLink>
        </section>
      </nav>
      <div class="admin-sidebar__footer">
        <SessionMenu inline />
      </div>
    </aside>
    <main class="admin-main">
      <div class="admin-main__topbar">
        <div class="topbar-left">
          <p class="breadcrumbs">Admin / {{ currentSection }}</p>
          <div class="global-alerts" v-if="activeAlerts.length > 0">
            <span v-for="(alert, idx) in activeAlerts" :key="idx">{{ alert }}</span>
          </div>
        </div>
        <div class="topbar-center">
          <input class="admin-search" placeholder="Search operators, creators, payouts…" />
        </div>
        <div class="topbar-right">
          <span class="role-badge">{{ roleLabel }}</span>
          <SessionMenu />
        </div>
      </div>
      <div class="admin-main__view">
        <RouterView />
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import SessionMenu from "../../components/SessionMenu.vue";
import { adminNav, normalizeAdminRole } from "../domain/permissions";
import { sessionState } from "../../stores/session";
import { adminState } from "../stores/adminState";

const route = useRoute();
const role = computed(() => normalizeAdminRole(sessionState.me?.role || "operator"));

const visibleNav = computed(() => {
  return adminNav.filter((item) => item.roles.includes(role.value));
});

const navGroups = computed(() => {
  const grouped = new Map<string, Array<(typeof adminNav)[number]>>();
  for (const item of visibleNav.value) {
    const bucket = grouped.get(item.section) || [];
    bucket.push(item);
    grouped.set(item.section, bucket);
  }
  return [...grouped.entries()].map(([section, items]) => ({ section, items }));
});

const currentSection = computed(() => String(route.meta.adminTitle || route.meta.adminMode || "Overview"));
const activeAlerts = computed(() => adminState.alerts.slice(0, 2));
const roleLabel = computed(() => {
  if (role.value === "super_admin") return "SUPER ADMIN";
  if (role.value === "finance_admin") return "FINANCE OPS";
  if (role.value === "support_admin") return "SUPPORT OPS";
  if (role.value === "moderator") return "MODERATION OPS";
  return "OPERATOR";
});
</script>

<style scoped>
.admin-shell { display: grid; grid-template-columns: 260px 1fr; min-height: 100dvh; }
.admin-sidebar { border-right: 1px solid rgba(255,255,255,.1); background: linear-gradient(180deg, rgba(8,12,28,.94), rgba(6,10,22,.92)); padding: 18px 14px; overflow-y: auto; }
.brand { display: grid; gap: 2px; padding: 10px 10px 16px; border-bottom: 1px solid rgba(255,255,255,.08); margin-bottom: 14px; }
.brand span { font-size: 12px; letter-spacing: .1em; text-transform: uppercase; color: rgba(255,255,255,.62); }
.brand strong { font-size: 19px; letter-spacing: -0.01em; }
.nav { display: grid; gap: 12px; }
.nav-group { display: grid; gap: 6px; }
.nav-group__title { margin: 0; padding: 0 10px; font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: rgba(255,255,255,.45); }
.nav-item { min-height: 40px; padding: 0 12px; border-radius: 10px; border: 1px solid transparent; display: flex; align-items: center; text-decoration: none; color: rgba(255,255,255,.72); font-size: 13px; }
.nav-item:hover { background: rgba(255,255,255,.05); color: rgba(255,255,255,.92); }
.nav-item.is-active { border-color: rgba(240,190,100,.3); color: #f4d8a7; background: linear-gradient(180deg, rgba(240,190,100,.2), rgba(240,190,100,.08)); }
.admin-sidebar__footer { margin-top: auto; padding-top: 12px; }
.admin-main { min-width: 0; height: 100dvh; overflow-y: auto; position: relative; }
.admin-main__topbar {
  position: sticky;
  top: 0;
  z-index: 16;
  display: grid;
  grid-template-columns: 1.3fr minmax(220px, .9fr) auto;
  align-items: start;
  gap: 12px;
  padding: 12px 20px 10px;
  border-bottom: 1px solid rgba(255,255,255,.08);
  background: linear-gradient(180deg, rgba(6,10,22,.92), rgba(6,10,22,.64));
  backdrop-filter: blur(12px);
}
.topbar-left { display: grid; gap: 8px; min-width: 0; }
.breadcrumbs { margin: 0; font-size: 11px; letter-spacing: .1em; text-transform: uppercase; color: rgba(255,255,255,.52); }
.global-alerts { display: flex; flex-wrap: wrap; gap: 6px; }
.global-alerts span { border-radius: 999px; padding: 4px 9px; font-size: 11px; border: 1px solid rgba(240,190,100,.3); color: rgba(245,218,162,.9); background: rgba(240,190,100,.1); }
.topbar-center { display: flex; justify-content: center; }
.admin-search { width: 100%; min-height: 38px; border-radius: 10px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.03); color: rgba(255,255,255,.88); padding: 0 12px; }
.topbar-right { display: flex; align-items: center; gap: 10px; justify-content: flex-end; }
.role-badge { border-radius: 999px; border: 1px solid rgba(168,199,255,.35); color: #c2d8ff; background: rgba(168,199,255,.08); min-height: 28px; padding: 0 10px; display: inline-flex; align-items: center; font-size: 10px; letter-spacing: .1em; text-transform: uppercase; font-weight: 600; }
.admin-main__view { padding: 0; }
.admin-main__view > :deep(.session-menu) { display: none; }
@media (max-width: 1023px) {
  .admin-shell { grid-template-columns: 1fr; }
  .admin-sidebar { position: sticky; top: 0; z-index: 10; border-right: 0; border-bottom: 1px solid rgba(255,255,255,.1); padding: 10px; }
  .brand { margin-bottom: 10px; }
  .nav { grid-auto-flow: column; grid-auto-columns: max-content; overflow-x: auto; }
  .nav-group { display: contents; }
  .nav-group__title { display: none; }
  .admin-sidebar__footer { margin-top: 10px; }
  .admin-main__topbar { grid-template-columns: 1fr; padding: 10px; }
  .topbar-center { order: 3; }
  .topbar-right { justify-content: flex-start; }
  .role-badge { display: none; }
}
</style>
