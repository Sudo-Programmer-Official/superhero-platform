<template>
  <section class="auth-view">
    <div class="auth-view__right">
      <AuthPanel :mode="mode" />
      <AppCard v-if="sessionState.statusText" muted class="auth-view__status">
        <p class="auth-view__status-label">Status</p>
        <p class="auth-view__status-copy">{{ sessionState.statusText }}</p>
      </AppCard>
    </div>

    <div class="auth-view__left">
      <h1 class="auth-view__title">
        Turn sessions into
        <span>shareable experiences</span>
        people book and redeem.
      </h1>
      <p class="auth-view__copy">
        Create offers, collect payments, and redeem in person from one premium flow.
      </p>

      <div class="auth-view__features">
        <div class="auth-feature" v-for="feature in features" :key="feature.title">
          <span class="auth-feature__icon">✦</span>
          <div>
            <p class="auth-feature__title">{{ feature.title }}</p>
            <p class="auth-feature__desc">{{ feature.desc }}</p>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import AppCard from "../design-system/primitives/AppCard.vue";
import AuthPanel from "../modules/auth/AuthPanel.vue";
import { sessionState } from "../stores/session";

withDefaults(
  defineProps<{
    mode?: "signin" | "signup";
  }>(),
  {
    mode: "signin"
  }
);

const features = [
  { title: "Publish in minutes", desc: "Launch offers quickly with premium presentation." },
  { title: "Share everywhere", desc: "Use one profile link across social and web." },
  { title: "Redeem confidently", desc: "Fast QR redemption and wallet-native check-in." }
];
</script>

<style scoped>
.auth-view {
  margin-inline: auto;
  display: grid;
  width: 100%;
  max-width: 1200px;
  align-items: start;
  gap: 24px;
  padding: calc(env(safe-area-inset-top, 0px) + 20px) 16px calc(env(safe-area-inset-bottom, 0px) + 20px);
  box-sizing: border-box;
}

.auth-view__right {
  width: 100%;
  max-width: 520px;
  justify-self: center;
}

.auth-view__status {
  margin-top: 16px;
}

.auth-view__status-label {
  margin: 0 0 4px;
  color: var(--accent);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.16em;
  text-transform: uppercase;
}

.auth-view__status-copy {
  margin: 0;
  color: var(--text-secondary);
  font-size: 14px;
}

.auth-view__left {
  max-width: 640px;
  padding: 32px 2px 40px;
}

.auth-view__title {
  margin: 0;
  font-size: clamp(34px, 10vw, 42px);
  font-weight: 800;
  line-height: 0.95;
  letter-spacing: -0.03em;
  max-width: 14ch;
}

.auth-view__title span {
  background: linear-gradient(115deg, var(--accent), var(--brand-violet));
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-family: "Times New Roman", serif;
  font-style: italic;
  font-weight: 700;
}

.auth-view__copy {
  margin: 20px 0 0;
  max-width: 48ch;
  color: rgba(255, 255, 255, 0.72);
  font-size: 16px;
  line-height: 1.55;
}

.auth-view__features {
  margin-top: 28px;
  display: grid;
  gap: 18px;
}

.auth-feature {
  display: flex;
  align-items: flex-start;
  gap: 12px;
}

.auth-feature__icon {
  display: grid;
  height: 32px;
  width: 32px;
  place-items: center;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  background: rgba(255, 255, 255, 0.04);
  color: var(--accent);
  font-size: 13px;
}

.auth-feature__title {
  margin: 0;
  font-size: 15px;
  font-weight: 600;
}

.auth-feature__desc {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: 14px;
  line-height: 1.55;
}

@media (max-width: 767px) {
  .auth-view {
    gap: 22px;
    padding: calc(env(safe-area-inset-top, 0px) + 20px) 16px calc(env(safe-area-inset-bottom, 0px) + 20px);
  }

  .auth-view__left {
    padding: 8px 2px 10px;
  }

  .auth-view__copy {
    margin-top: 16px;
    font-size: 15px;
  }

  .auth-view__features {
    margin-top: 22px;
    gap: 14px;
  }
}

@media (min-width: 768px) {
  .auth-view {
    padding: calc(env(safe-area-inset-top, 0px) + 32px) 24px calc(env(safe-area-inset-bottom, 0px) + 32px);
  }
}

@media (min-width: 1024px) {
  .auth-view {
    min-height: calc(100vh - 72px);
    align-items: center;
    gap: 64px;
    padding: 32px 0;
    grid-template-columns: 1.1fr 0.9fr;
  }

  .auth-view__left {
    order: 1;
  }

  .auth-view__right {
    order: 2;
    justify-self: end;
  }

  .auth-view__title {
    font-size: clamp(44px, 5vw, 64px);
  }

  .auth-view__copy {
    margin-top: 24px;
    font-size: 18px;
    line-height: 1.6;
  }

  .auth-view__features {
    margin-top: 32px;
  }
}
</style>
