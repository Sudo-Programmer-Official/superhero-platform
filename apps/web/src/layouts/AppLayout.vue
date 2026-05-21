<template>
  <div class="layout-shell">
    <div class="bg-orb bg-orb-a" aria-hidden="true"></div>
    <div class="bg-orb bg-orb-b" aria-hidden="true"></div>

    <header class="app-header">
      <div class="app-header-inner content-wrap">
        <div>
          <p class="eyebrow">In-Person Superhero</p>
          <h1 class="app-title">Production foundation</h1>
          <p class="subtitle">Route guards, tenant-aware API, bootstrap onboarding, and PWA base are wired.</p>
        </div>
        <button v-if="sessionState.user" class="ghost-btn" @click="onLogout">Sign out</button>
      </div>
    </header>

    <div class="app-body content-wrap">
      <aside class="app-nav-desktop" aria-label="Primary">
        <RouterLink class="nav-btn" :class="{ active: route.name === 'home' }" to="/">Home</RouterLink>
        <RouterLink class="nav-btn" :class="{ active: route.name === 'deals' }" to="/deals">Deals</RouterLink>
        <RouterLink class="nav-btn" :class="{ active: route.name === 'profile' }" to="/profile">Profile</RouterLink>
      </aside>

      <main class="app-main" role="main">
        <RouterView />
      </main>
    </div>

    <nav class="app-nav-mobile" aria-label="Primary">
      <RouterLink class="nav-btn" :class="{ active: route.name === 'home' }" to="/">Home</RouterLink>
      <RouterLink class="nav-btn" :class="{ active: route.name === 'deals' }" to="/deals">Deals</RouterLink>
      <RouterLink class="nav-btn" :class="{ active: route.name === 'profile' }" to="/profile">Profile</RouterLink>
      <RouterLink class="nav-btn" :class="{ active: route.name === 'auth' }" to="/auth">Auth</RouterLink>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { logout } from "../firebase/auth";
import { sessionState } from "../stores/session";

const route = useRoute();

async function onLogout() {
  await logout();
  sessionState.me = null;
}
</script>
