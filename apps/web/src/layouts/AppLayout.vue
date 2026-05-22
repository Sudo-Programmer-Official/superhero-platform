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
          <button class="sidebar__item" type="button">Bookings</button>
          <button class="sidebar__item" type="button">Wallet Passes</button>
          <button class="sidebar__item" type="button">Redemptions</button>
          <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'profile' }" to="/dashboard/profile">Profile</RouterLink>
          <button class="sidebar__item" type="button">Payouts</button>
          <button class="sidebar__item" type="button">Settings</button>
        </nav>

        <div class="sidebar__profile">
          <img src="https://images.unsplash.com/photo-1542204625-de293a5df31c?auto=format&fit=crop&w=120&q=80" alt="Marla profile" />
          <div>
            <p>Marla B.</p>
            <span>View profile</span>
          </div>
        </div>
      </aside>

      <main class="dashboard-main">
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
        <button class="sidebar__item" type="button">Bookings</button>
        <button class="sidebar__item" type="button">Wallet Passes</button>
        <button class="sidebar__item" type="button">Redemptions</button>
        <RouterLink class="sidebar__item" :class="{ 'is-active': route.name === 'profile' }" to="/dashboard/profile" @click="isDrawerOpen = false">Profile</RouterLink>
      </nav>

      <AppButton v-if="sessionState.user" variant="secondary" size="md" context="form" @click="onLogout">Sign out</AppButton>
    </aside>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppButton from "../design-system/primitives/AppButton.vue";
import GradientOrb from "../design-system/primitives/GradientOrb.vue";
import { logout } from "../firebase/auth";
import { sessionState } from "../stores/session";

const route = useRoute();
const router = useRouter();
const isDrawerOpen = ref(false);

async function onLogout() {
  await logout();
  sessionState.me = null;
  sessionState.user = null;
  sessionState.token = null;
  isDrawerOpen.value = false;
  await router.push("/signin");
}
</script>

<style scoped>
.app-shell {
  position: relative;
  min-height: calc(100dvh - var(--safe-top));
  overflow-x: clip;
  padding: 24px 28px 28px;
}

.dashboard-layout {
  margin: 0 auto;
  max-width: 1440px;
  display: grid;
  grid-template-columns: 260px 1fr;
  gap: 24px;
}

.sidebar {
  min-height: calc(100dvh - 56px);
  display: flex;
  flex-direction: column;
  padding: 24px 18px;
  border-radius: 28px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(8, 12, 28, 0.92), rgba(5, 10, 24, 0.86));
  backdrop-filter: blur(18px);
  box-shadow: 0 8px 40px rgba(0, 0, 0, 0.24);
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
  transition: all 180ms ease;
}

.sidebar__item:hover {
  background: rgba(255, 255, 255, 0.04);
  color: rgba(255, 255, 255, 0.92);
}

.sidebar__item.is-active {
  color: #f4d8a7;
  border-color: rgba(240, 190, 100, 0.22);
  background: linear-gradient(180deg, rgba(240, 190, 100, 0.22), rgba(240, 190, 100, 0.12));
}

.sidebar__profile {
  margin-top: auto;
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.03);
  display: flex;
  align-items: center;
  gap: 12px;
}

.sidebar__profile img {
  width: 44px;
  height: 44px;
  border-radius: 999px;
  object-fit: cover;
}

.sidebar__profile p {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
}

.sidebar__profile span {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.62);
}

.dashboard-main {
  min-width: 0;
}

.drawer-toggle,
.drawer-overlay,
.drawer {
  display: none;
}

@media (max-width: 1023px) {
  .app-shell {
    padding: 16px 20px 24px;
  }

  .dashboard-layout {
    grid-template-columns: 1fr;
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
}
</style>
