<template>
  <div v-if="inline" class="menu-inline">
    <div class="menu-inline__identity">
      <div class="avatar">{{ initials }}</div>
      <div>
        <p>{{ displayName }}</p>
        <span>{{ roleLabel }}</span>
      </div>
      <span v-if="isSuperAdmin" class="admin-badge">Admin Mode</span>
    </div>
    <div class="menu-inline__actions">
      <RouterLink v-for="item in menuItems" :key="item.label" class="menu-link" :to="item.to" @click="$emit('navigate')">
        {{ item.label }}
      </RouterLink>
      <button class="menu-link menu-link--danger" type="button" @click="onLogout">Logout</button>
    </div>
  </div>

  <details v-else class="session-menu">
    <summary class="session-trigger">
      <div class="avatar">{{ initials }}</div>
      <div class="identity">
        <p>{{ displayName }}</p>
        <span>{{ roleLabel }}</span>
      </div>
      <span v-if="isSuperAdmin" class="admin-badge">Admin Mode</span>
    </summary>
    <div class="session-dropdown">
      <RouterLink v-for="item in menuItems" :key="item.label" class="menu-link" :to="item.to">{{ item.label }}</RouterLink>
      <button v-if="!isAdminRole" class="menu-link menu-link--muted" type="button" disabled>Switch Workspace (Soon)</button>
      <button class="menu-link menu-link--danger" type="button" @click="onLogout">Logout</button>
    </div>
  </details>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import { logout } from "../firebase/auth";
import { canAccessAdminRole } from "../admin/domain/permissions";
import { resetDealStudio } from "../stores/dealStudio";
import { clearSessionState, sessionState } from "../stores/session";
import { clearToasts } from "../stores/toast";

const props = withDefaults(defineProps<{ inline?: boolean }>(), { inline: false });
defineEmits<{ navigate: [] }>();

const router = useRouter();

const role = computed(() => sessionState.me?.role || "practitioner");
const isSuperAdmin = computed(() => role.value === "super_admin");
const isAdminRole = computed(() => canAccessAdminRole(role.value));

const displayName = computed(() => {
  return sessionState.user?.displayName?.trim() || sessionState.me?.practitioner_name?.trim() || sessionState.me?.email || "OpenMat User";
});

const roleLabel = computed(() => {
  if (isSuperAdmin.value) return "Super Admin";
  if (role.value === "support_admin") return "Support Admin";
  if (role.value === "finance_admin") return "Finance Admin";
  if (role.value === "moderator") return "Moderator";
  if (role.value === "operator" || role.value === "admin") return "Operator";
  return "Practitioner";
});

const initials = computed(() => {
  const parts = displayName.value.split(/\s+/).filter(Boolean).slice(0, 2);
  return parts.map((part) => part[0]?.toUpperCase() || "").join("") || "OM";
});

const menuItems = computed(() => {
  if (isAdminRole.value) {
    return [
      { label: "Admin Overview", to: { name: "admin-overview" } },
      { label: "Settings", to: { name: "admin-settings" } }
    ];
  }
  return [
    { label: "View Profile", to: { name: "profile" } },
    { label: "Settings", to: { name: "settings" } }
  ];
});

async function onLogout() {
  try {
    await logout();
  } finally {
    clearToasts();
    resetDealStudio();
    clearSessionState();
    await router.push("/signin");
  }
}
</script>

<style scoped>
.session-menu { position: relative; }
.session-trigger {
  list-style: none;
  display: flex;
  align-items: center;
  gap: 10px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.06), rgba(255, 255, 255, 0.02));
  padding: 8px 10px;
  cursor: pointer;
}
.session-trigger::-webkit-details-marker { display: none; }
.identity p { margin: 0; font-size: 13px; font-weight: 600; }
.identity span { display: block; margin-top: 2px; font-size: 11px; color: rgba(255, 255, 255, 0.64); }
.avatar {
  width: 34px;
  height: 34px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  color: #f4d8a7;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  background: linear-gradient(145deg, rgba(244, 201, 125, 0.25), rgba(95, 73, 44, 0.38));
  border: 1px solid rgba(240, 190, 100, 0.34);
}
.admin-badge {
  border-radius: 999px;
  border: 1px solid rgba(240, 190, 100, 0.35);
  color: #f4d8a7;
  font-size: 10px;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  padding: 3px 7px;
}
.session-dropdown {
  position: absolute;
  right: 0;
  top: calc(100% + 8px);
  min-width: 220px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(8, 14, 28, 0.9);
  backdrop-filter: blur(16px);
  padding: 8px;
  display: grid;
  gap: 4px;
  z-index: 30;
}
.menu-link {
  min-height: 34px;
  border-radius: 10px;
  border: 1px solid transparent;
  color: rgba(255, 255, 255, 0.82);
  text-decoration: none;
  background: transparent;
  display: flex;
  align-items: center;
  justify-content: flex-start;
  padding: 0 10px;
  font-size: 13px;
}
.menu-link:hover { background: rgba(255, 255, 255, 0.05); }
.menu-link--muted { color: rgba(255, 255, 255, 0.42); }
.menu-link--danger { color: #ffb5b5; }

.menu-inline {
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.03);
  padding: 10px;
  display: grid;
  gap: 10px;
}
.menu-inline__identity {
  display: flex;
  align-items: center;
  gap: 10px;
}
.menu-inline__identity p { margin: 0; font-size: 14px; font-weight: 600; }
.menu-inline__identity span { font-size: 12px; color: rgba(255, 255, 255, 0.66); }
.menu-inline__actions {
  display: grid;
  gap: 6px;
}
</style>
