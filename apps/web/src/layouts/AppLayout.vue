<template>
  <div class="app-shell">
    <GradientOrb tone="violet" size="lg" position="-right-24 top-20" />
    <GradientOrb tone="gold" size="md" position="-left-16 top-52" />

    <div class="dashboard-layout">
      <aside class="sidebar">
        <div class="sidebar__brand">
          <span class="sidebar__brand-icon">O</span>
          <span class="sidebar__brand-text">OpenMat</span>
        </div>

        <nav class="sidebar__nav">
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'dashboard' }" to="/dashboard">Home</RouterLink>
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'deals' }" to="/dashboard/deals">Deals</RouterLink>
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'bookings' }" to="/dashboard/bookings">Bookings</RouterLink>
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'wallet-passes' }" to="/dashboard/wallet-passes">Wallet Passes</RouterLink>
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'redemptions' }" to="/dashboard/redemptions">Redemptions</RouterLink>
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'profile' }" to="/dashboard/profile">Profile</RouterLink>
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'payouts' }" to="/dashboard/payouts">Payouts</RouterLink>
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'settings' }" to="/dashboard/settings">Settings</RouterLink>
        </nav>

        <RouterLink class="sidebar__profile" to="/dashboard/profile">
          <img
            v-if="avatarSrc && !avatarErrored"
            :src="avatarSrc"
            :alt="`${displayName} profile`"
            @error="avatarErrored = true"
          />
          <div v-else class="sidebar__avatar-fallback">{{ avatarInitials }}</div>
          <div>
            <p>{{ displayName }}</p>
            <span>View profile</span>
          </div>
        </RouterLink>
      </aside>

      <main class="dashboard-main">
        <div class="dashboard-main__topbar">
          <SessionMenu />
        </div>
        <RouterView />
      </main>
    </div>

    <button class="drawer-toggle" type="button" aria-label="Open sidebar menu" @click="isDrawerOpen = true">☰</button>
    <div class="drawer-overlay" :class="{ 'is-open': isDrawerOpen }" @click="isDrawerOpen = false"></div>
    <aside class="drawer" :class="{ 'is-open': isDrawerOpen }" aria-label="Mobile dashboard navigation">
      <div class="sidebar__brand">
        <span class="sidebar__brand-icon">O</span>
        <span class="sidebar__brand-text">OpenMat</span>
      </div>

      <nav class="sidebar__nav">
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'dashboard' }" to="/dashboard" @click="isDrawerOpen = false">Home</RouterLink>
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'deals' }" to="/dashboard/deals" @click="isDrawerOpen = false">Deals</RouterLink>
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'bookings' }" to="/dashboard/bookings" @click="isDrawerOpen = false">Bookings</RouterLink>
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'wallet-passes' }" to="/dashboard/wallet-passes" @click="isDrawerOpen = false">Wallet Passes</RouterLink>
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'redemptions' }" to="/dashboard/redemptions" @click="isDrawerOpen = false">Redemptions</RouterLink>
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'profile' }" to="/dashboard/profile" @click="isDrawerOpen = false">Profile</RouterLink>
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'payouts' }" to="/dashboard/payouts" @click="isDrawerOpen = false">Payouts</RouterLink>
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'settings' }" to="/dashboard/settings" @click="isDrawerOpen = false">Settings</RouterLink>
      </nav>

      <div class="drawer-footer">
        <SessionMenu inline @navigate="isDrawerOpen = false" />
      </div>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRoute } from "vue-router";
import SessionMenu from "../components/SessionMenu.vue";
import GradientOrb from "../design-system/primitives/GradientOrb.vue";
import { sessionState } from "../stores/session";

const route = useRoute();
const isDrawerOpen = ref(false);
const avatarErrored = ref(false);

const displayName = computed(() => {
  return sessionState.user?.displayName?.trim() || sessionState.me?.practitioner_name?.trim() || "Demo User";
});

const avatarSrc = computed(() => sessionState.user?.photoURL || "");

const avatarInitials = computed(() => {
  const parts = displayName.value
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2);
  return parts.map((part) => part[0]?.toUpperCase() || "").join("") || "DU";
});
</script>

<style scoped>
.app-shell {
  position: relative;
  height: 100dvh;
  overflow-x: clip;
  overflow-y: hidden;
  width: 100%;
  padding: 0;
}

.dashboard-layout {
  width: 100%;
  height: 100dvh;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 0;
  padding: 0;
  box-sizing: border-box;
  overflow: hidden;
}

.sidebar {
  height: 100dvh;
  display: flex;
  flex-direction: column;
  padding: 24px 16px 18px;
  border-radius: 0;
  border: 1px solid rgba(255, 255, 255, 0.07);
  border-left: 0;
  border-top: 0;
  border-bottom: 0;
  background: linear-gradient(180deg, rgba(8, 12, 28, 0.92), rgba(5, 10, 24, 0.86));
  backdrop-filter: blur(18px);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.24);
  overflow-y: auto;
}

.sidebar__brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 32px;
}

.sidebar__brand-icon {
  width: 32px;
  height: 32px;
  border-radius: 12px;
  display: grid;
  place-items: center;
  color: #f2c67a;
  font-weight: 700;
  background: linear-gradient(145deg, rgba(244, 201, 125, 0.3), rgba(201, 141, 67, 0.12));
  box-shadow: 0 0 24px rgba(240, 190, 100, 0.2);
}

.sidebar__brand-text {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
}

.sidebar__nav {
  display: grid;
  gap: 8px;
}

.sidebar__item {
  height: 48px;
  border-radius: 14px;
  padding: 0 14px;
  border: 1px solid transparent;
  color: rgba(255, 255, 255, 0.72);
  background: transparent;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  font-weight: 500;
  text-decoration: none;
  transition: all 180ms ease, transform 180ms ease;
}

.sidebar__item:hover {
  transform: translateY(-1px);
  background: rgba(255, 255, 255, 0.045);
  color: rgba(255, 255, 255, 0.92);
}

.sidebar__item.is-active {
  color: #f4d8a7;
  border-color: rgba(240, 190, 100, 0.2);
  background: linear-gradient(180deg, rgba(240, 190, 100, 0.18), rgba(240, 190, 100, 0.1));
  box-shadow: inset 0 0 0 1px rgba(240, 190, 100, 0.08), 0 0 14px rgba(240, 190, 100, 0.12);
}

.sidebar__profile {
  margin-top: auto;
  padding: 12px;
  border-radius: 18px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.045), rgba(255, 255, 255, 0.02));
  display: flex;
  align-items: center;
  gap: 12px;
  text-decoration: none;
  transition: background 180ms ease, transform 180ms ease, border-color 180ms ease;
}

.sidebar__profile:hover {
  transform: translateY(-1px);
  border-color: rgba(240, 190, 100, 0.24);
  background: linear-gradient(180deg, rgba(240, 190, 100, 0.08), rgba(255, 255, 255, 0.04));
}

.sidebar__profile img {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  object-fit: cover;
}

.sidebar__avatar-fallback {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  color: #f4d8a7;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.06em;
  background: linear-gradient(145deg, rgba(244, 201, 125, 0.25), rgba(95, 73, 44, 0.38));
  border: 1px solid rgba(240, 190, 100, 0.34);
}

.sidebar__profile p {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: rgba(255, 255, 255, 0.94);
}

.sidebar__profile span {
  display: block;
  margin-top: 2px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.66);
}

.dashboard-main {
  min-width: 0;
  height: 100dvh;
  padding: 0;
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
}

.dashboard-main__topbar {
  position: sticky;
  top: 0;
  z-index: 18;
  display: flex;
  justify-content: flex-end;
  padding: 10px 16px 0;
  pointer-events: none;
}

.dashboard-main__topbar :deep(.session-menu) {
  pointer-events: auto;
}

.drawer-toggle,
.drawer-overlay,
.drawer {
  display: none;
}

@media (max-width: 1023px) {
  .app-shell {
    padding: 0;
  }

  .dashboard-layout {
    grid-template-columns: 1fr;
    height: 100dvh;
    padding: 0;
  }

  .sidebar {
    display: none;
  }

  .drawer-toggle {
    display: grid;
    place-items: center;
    position: fixed;
    right: 20px;
    top: 16px;
    width: 48px;
    height: 48px;
    z-index: 60;
    border: 0;
    border-radius: 16px;
    color: rgba(255, 255, 255, 0.9);
    font-size: 22px;
    background: rgba(255, 255, 255, 0.03);
    box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
  }

  .drawer-overlay {
    position: fixed;
    inset: 0;
    z-index: 69;
    background: rgba(5, 9, 19, 0.58);
    backdrop-filter: blur(6px);
    opacity: 0;
    pointer-events: none;
    transition: opacity 180ms ease;
  }

  .drawer-overlay.is-open {
    opacity: 1;
    pointer-events: auto;
  }

  .drawer {
    position: fixed;
    top: 0;
    right: 0;
    bottom: 0;
    width: 280px;
    z-index: 70;
    padding: 24px 18px;
    display: flex;
    flex-direction: column;
    gap: 16px;
    transform: translateX(100%);
    opacity: 0;
    transition: transform 220ms ease, opacity 220ms ease;
    background: rgba(7, 14, 28, 0.96);
    backdrop-filter: blur(20px);
    border-left: 1px solid rgba(255, 255, 255, 0.08);
  }

  .drawer.is-open {
    transform: translateX(0);
    opacity: 1;
  }

  .drawer-footer {
    margin-top: auto;
  }

  .dashboard-main__topbar {
    padding: 10px 76px 0 10px;
  }
}

@media (min-width: 1024px) and (max-width: 1279px) {
  .dashboard-layout {
    grid-template-columns: 220px 1fr;
    gap: 0;
    padding: 0;
  }

  .sidebar {
    padding: 22px 12px 14px;
  }

  .sidebar__item {
    height: 44px;
    padding-inline: 12px;
    font-size: 14px;
  }
}
</style>
