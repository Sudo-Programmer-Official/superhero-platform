<template>
  <AppShell>
    <div class="bg-orb bg-orb-a" aria-hidden="true"></div>
    <div class="bg-orb bg-orb-b" aria-hidden="true"></div>

    <section class="phone-frame">
      <header class="zone zone-topbar">
        <p class="eyebrow">In-Person Superhero</p>
        <button v-if="sessionState.user" class="ghost-btn" @click="onLogout">Sign out</button>
      </header>

      <section class="zone zone-hero">
        <p class="kicker">Platform</p>
        <h1>Production foundation</h1>
        <p class="subtitle">Route guards, tenant-aware API, bootstrap onboarding, and PWA base are wired.</p>
      </section>

      <RouterView />

      <nav class="zone zone-bottom-nav" aria-label="Primary">
        <RouterLink class="nav-btn" :class="{ active: route.name === 'home' }" to="/">Home</RouterLink>
        <RouterLink class="nav-btn" :class="{ active: route.name === 'deals' }" to="/deals">Deals</RouterLink>
        <RouterLink class="nav-btn" :class="{ active: route.name === 'profile' }" to="/profile">Profile</RouterLink>
        <RouterLink class="nav-btn" :class="{ active: route.name === 'auth' }" to="/auth">Auth</RouterLink>
      </nav>
    </section>
  </AppShell>
</template>

<script setup lang="ts">
import { useRoute } from "vue-router";
import { logout } from "./firebase/auth";
import AppShell from "./layouts/AppShell.vue";
import { sessionState } from "./stores/session";

const route = useRoute();

async function onLogout() {
  await logout();
  sessionState.me = null;
}
</script>
