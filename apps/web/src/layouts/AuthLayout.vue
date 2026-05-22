<template>
  <div class="relative min-h-[calc(100dvh-var(--safe-top))] overflow-x-clip">
    <GradientOrb tone="gold" size="md" position="left-[-72px] top-[84px]" />
    <GradientOrb tone="violet" size="sm" position="right-[8%] top-[18%]" />

    <div
      class="pointer-events-none absolute inset-x-0 top-0 h-[288px] bg-[radial-gradient(120%_80%_at_50%_0%,rgba(248,213,147,0.16),transparent_68%)]"
      aria-hidden="true"
    ></div>
    <div
      class="pointer-events-none absolute -right-20 top-1/3 h-[288px] w-[288px] rounded-full bg-[radial-gradient(circle,rgba(211,159,84,0.21),transparent_66%)] blur-2xl"
      aria-hidden="true"
    ></div>
    <div
      class="pointer-events-none absolute inset-x-0 bottom-0 h-[208px] bg-[linear-gradient(to_top,rgba(3,7,14,.86),rgba(3,7,14,.12)_56%,transparent)]"
      aria-hidden="true"
    ></div>
    <div
      class="pointer-events-none absolute inset-0 opacity-[0.055] [background-image:radial-gradient(rgba(255,255,255,.85)_0.5px,transparent_0.5px)] [background-size:3px_3px]"
      aria-hidden="true"
    ></div>

    <header class="sticky top-0 z-30 h-[72px] border-b border-[rgba(255,255,255,0.08)] bg-[rgba(10,15,25,0.52)] backdrop-blur-2xl">
      <div class="top-nav__inner mx-auto flex h-full w-full max-w-[1280px] items-center justify-between px-5 lg:px-8">
        <RouterLink class="brand no-underline" to="/">
          <span class="brand__icon">O</span>
          <span class="brand__text">OpenMat</span>
        </RouterLink>

        <nav v-if="isDesktop" class="hidden items-center justify-center gap-8 text-[14px] text-[rgba(255,255,255,0.78)] lg:flex">
          <a class="no-underline text-inherit transition-colors duration-150 hover:text-white" href="#">Product</a>
          <a class="no-underline text-inherit transition-colors duration-150 hover:text-white" href="#">Creators</a>
          <a class="no-underline text-inherit transition-colors duration-150 hover:text-white" href="#">Pricing</a>
          <a class="no-underline text-inherit transition-colors duration-150 hover:text-white" href="#">Resources</a>
        </nav>

        <button
          v-else
          class="mobile-menu-btn"
          type="button"
          aria-label="Open navigation menu"
          @click="drawerOpen = true"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M5 7h14M5 12h14M5 17h14" />
          </svg>
        </button>
      </div>
    </header>

    <div
      v-if="!isDesktop"
      class="mobile-drawer-overlay"
      :class="drawerOpen ? 'mobile-drawer-overlay--open' : ''"
      @click="drawerOpen = false"
    ></div>
    <aside
      v-if="!isDesktop"
      class="mobile-drawer"
      :class="drawerOpen ? 'mobile-drawer--open' : ''"
      aria-label="Mobile navigation"
    >
      <div class="mobile-drawer__head">
        <p class="mobile-drawer__title">Menu</p>
        <button class="mobile-drawer__close" type="button" aria-label="Close navigation menu" @click="drawerOpen = false">×</button>
      </div>
      <nav class="mobile-drawer__nav">
        <AppButton tag="RouterLink" to="/signin" variant="secondary" size="form" @click="drawerOpen = false">Login</AppButton>
        <AppButton tag="RouterLink" to="/signup" variant="primary" size="form" @click="drawerOpen = false">Start free</AppButton>
        <a href="#" @click="drawerOpen = false">Product</a>
        <a href="#" @click="drawerOpen = false">Pricing</a>
        <a href="#" @click="drawerOpen = false">Resources</a>
      </nav>
    </aside>

    <AppContainer>
      <main class="py-4 md:py-8 lg:py-[64px]" role="main">
        <RouterView v-slot="{ Component, route }">
          <Transition name="auth-page" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </Transition>
        </RouterView>
      </main>
    </AppContainer>
  </div>
</template>

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppContainer from "../design-system/primitives/AppContainer.vue";
import GradientOrb from "../design-system/primitives/GradientOrb.vue";

const drawerOpen = ref(false);
const isDesktop = ref(typeof window !== "undefined" ? window.innerWidth >= 1024 : true);

function syncViewport() {
  isDesktop.value = window.innerWidth >= 1024;
  if (isDesktop.value) drawerOpen.value = false;
}

onMounted(() => {
  syncViewport();
  window.addEventListener("resize", syncViewport);
});

onBeforeUnmount(() => {
  window.removeEventListener("resize", syncViewport);
});
</script>

<style scoped>
.brand {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  margin-left: 2px;
}

.brand__icon {
  display: grid;
  width: 16px;
  height: 16px;
  place-items: center;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.2);
  background: linear-gradient(145deg, rgba(244, 201, 125, 0.24), rgba(211, 159, 84, 0.14));
  color: var(--accent);
  font-size: 10px;
  font-weight: 700;
}

.brand__text {
  color: var(--text-primary);
  font-size: 18px;
  font-weight: 700;
  letter-spacing: -0.03em;
}

.mobile-menu-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border: 0;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.03);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.06);
  color: var(--text-primary);
  transition: background 180ms ease;
  margin-right: 2px;
}

.mobile-menu-btn:hover,
.mobile-menu-btn:active {
  background: rgba(255, 255, 255, 0.06);
}

.mobile-menu-btn svg {
  width: 22px;
  height: 22px;
  stroke: currentColor;
  stroke-width: 2;
  fill: none;
  stroke-linecap: round;
}

.mobile-drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 39;
  background: rgba(2, 5, 12, 0.42);
  opacity: 0;
  pointer-events: none;
  transition: opacity 220ms ease;
}

.mobile-drawer-overlay--open {
  opacity: 1;
  pointer-events: auto;
}

.mobile-drawer {
  position: fixed;
  top: 0;
  right: 0;
  z-index: 40;
  width: 280px;
  height: 100dvh;
  background: rgba(7, 14, 28, 0.96);
  backdrop-filter: blur(20px);
  border-left: 1px solid rgba(255, 255, 255, 0.12);
  transform: translateX(100%);
  opacity: 0;
  transition: transform 240ms ease, opacity 240ms ease;
  padding: 24px;
}

.mobile-drawer--open {
  transform: translateX(0);
  opacity: 1;
}

.mobile-drawer__head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 24px;
}

.mobile-drawer__title {
  margin: 0;
  font-size: 14px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.72);
}

.mobile-drawer__close {
  border: 0;
  background: transparent;
  color: var(--text-primary);
  font-size: 28px;
  line-height: 1;
}

.mobile-drawer__nav {
  display: grid;
  gap: 24px;
}

.mobile-drawer__nav a {
  color: var(--text-primary);
  text-decoration: none;
  font-size: 16px;
}

.auth-page-enter-active,
.auth-page-leave-active {
  transition: opacity 220ms ease, transform 220ms ease;
}

.auth-page-enter-from,
.auth-page-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

@media (min-width: 1024px) {
  .top-nav__inner {
    padding-left: 32px;
    padding-right: 32px;
  }

  .brand {
    gap: 10px;
    margin-left: 0;
  }

  .brand__icon {
    width: 18px;
    height: 18px;
  }

  .nav-actions--desktop {
    display: flex !important;
  }

  .mobile-menu-btn {
    display: none;
  }

  .mobile-drawer,
  .mobile-drawer-overlay {
    display: none;
  }
}

@media (max-width: 1023px) {
  .top-nav__inner {
    padding-left: 20px;
    padding-right: 20px;
  }
}

@media (max-width: 1023px) {
  .nav-actions--desktop {
    display: none !important;
  }

  .mobile-menu-btn {
    display: inline-flex;
  }
}
</style>
