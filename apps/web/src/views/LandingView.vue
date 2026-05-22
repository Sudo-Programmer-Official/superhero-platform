<template>
  <div class="landing-view">
    <GradientOrb tone="violet" position="-right-24 top-24" />
    <GradientOrb tone="gold" size="md" position="left-24 top-64" />

    <header class="landing-header sticky top-0 z-40 h-[72px] border-b border-[rgba(255,255,255,0.06)] bg-[linear-gradient(180deg,rgba(7,12,22,0.82),rgba(7,12,22,0.45))] backdrop-blur-[18px]">
      <div class="landing-header__inner mx-auto flex h-full w-full max-w-[1520px] items-center justify-between px-4 py-3 md:px-8 xl:px-12 2xl:px-16">
        <a class="brand no-underline" href="#">
          <span class="brand__icon">O</span>
          <span class="brand__text">OpenMat</span>
        </a>

        <nav class="hidden items-center justify-center gap-8 text-[14px] text-[rgba(255,255,255,0.78)] lg:flex">
          <a class="no-underline text-inherit" href="#">Product</a>
          <a class="no-underline text-inherit" href="#">For Creators</a>
          <a class="no-underline text-inherit" href="#">Pricing</a>
          <a class="no-underline text-inherit" href="#">Resources</a>
          <a class="no-underline text-inherit" href="#">About</a>
        </nav>

        <div class="nav-actions hidden lg:flex">
          <AppButton tag="RouterLink" to="/signin" variant="secondary" size="nav" context="navbar">Log in</AppButton>
          <AppButton tag="RouterLink" to="/signup" variant="primary" size="nav" context="navbar">Start free</AppButton>
        </div>

        <button class="mobile-menu-btn flex lg:hidden" type="button" aria-label="Open menu" @click="drawerOpen = true">☰</button>
      </div>
    </header>
    <div class="mobile-drawer-overlay" :class="{ 'mobile-drawer-overlay--open': drawerOpen }" @click="drawerOpen = false"></div>
    <aside class="mobile-drawer" :class="{ 'mobile-drawer--open': drawerOpen }" aria-label="Mobile navigation">
      <div class="mobile-drawer__head">
        <p class="mobile-drawer__title">Menu</p>
        <button class="mobile-drawer__close" type="button" aria-label="Close menu" @click="drawerOpen = false">×</button>
      </div>
      <nav class="mobile-drawer__nav">
        <AppButton tag="RouterLink" to="/signin" variant="secondary" size="form" @click="drawerOpen = false">Login</AppButton>
        <AppButton tag="RouterLink" to="/signup" variant="primary" size="form" @click="drawerOpen = false">Start free</AppButton>
        <a href="#" @click="drawerOpen = false">Product</a>
        <a href="#" @click="drawerOpen = false">Pricing</a>
        <a href="#" @click="drawerOpen = false">Resources</a>
      </nav>
    </aside>

    <section class="hero-section">
      <AppContainer>
        <div class="hero-shell">
          <div class="hero-grid">
            <div class="hero-copy">
              <p class="hero-kicker">For wellness creators</p>
              <h1 class="hero-title">
                Turn sessions into
                <span class="hero-title__accent">shareable experiences</span>
                people book and redeem.
              </h1>
              <p class="hero-subcopy">Create offers, collect payments, issue wallet passes, and redeem in person from your phone.</p>

              <div class="hero-cta-row">
                <AppButton class="hero-cta-btn" tag="RouterLink" to="/signup" variant="primary">Start as a practitioner</AppButton>
                <AppButton class="hero-cta-btn" tag="RouterLink" to="/openmat/marla-therapist" variant="secondary">View demo profile</AppButton>
              </div>

              <div class="hero-trust-row">
                <div class="hero-avatars">
                  <img class="hero-avatar" src="https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=120&q=80" alt="Creator avatar 1" />
                  <img class="hero-avatar" src="https://images.unsplash.com/photo-1542204625-de293a5df31c?auto=format&fit=crop&w=120&q=80" alt="Creator avatar 2" />
                  <img class="hero-avatar" src="https://images.unsplash.com/photo-1531891437562-4301cf35b7e4?auto=format&fit=crop&w=120&q=80" alt="Creator avatar 3" />
                  <img class="hero-avatar" src="https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=120&q=80" alt="Creator avatar 4" />
                  <img class="hero-avatar" src="https://images.unsplash.com/photo-1557862921-37829c790f19?auto=format&fit=crop&w=120&q=80" alt="Creator avatar 5" />
                </div>
                <p class="hero-rating">Loved by 2,000+ wellness creators</p>
                <div class="hero-stars-group">
                  <p class="hero-stars">★★★★★</p>
                  <p class="hero-score">4.9/5</p>
                </div>
              </div>
            </div>

            <div class="hero-media">
              <div class="hero-left-blue-ambient" aria-hidden="true"></div>
              <div class="hero-violet-ambient" aria-hidden="true"></div>
              <div class="hero-arc-glow" aria-hidden="true"></div>
              <div class="hero-hotspot" aria-hidden="true"></div>

              <div class="hero-visual-grid">
                <div class="hero-phone-wrap">
                  <div class="hero-phone">
                    <div class="hero-phone__island"></div>
                    <div class="hero-phone__content">
                      <p class="hero-phone__hello">Hi, Marla 👋</p>
                      <p class="hero-phone__muted">Here's what's happening</p>
                      <p class="hero-phone__today">Today</p>
                      <div class="hero-phone__upcoming">
                        <p class="hero-phone__upcoming-title">Breathwork Journey</p>
                        <p class="hero-phone__upcoming-meta">7:00 PM · 6 seats left</p>
                      </div>

                      <p class="hero-phone__section-title">Your deals</p>
                      <div class="hero-phone__deal-list">
                        <div class="hero-phone__deal-row">
                          <img src="https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=80&q=80" alt="" />
                          <div>
                            <p>Morning Flow</p>
                            <span>$55 · Yoga Class</span>
                          </div>
                          <b>Published</b>
                        </div>
                        <div class="hero-phone__deal-row">
                          <img src="https://images.unsplash.com/photo-1593811167562-9cef47bfc4d7?auto=format&fit=crop&w=80&q=80" alt="" />
                          <div>
                            <p>Sound Bath</p>
                            <span>$49 · Shared healing</span>
                          </div>
                          <i>Draft</i>
                        </div>
                        <div class="hero-phone__deal-row">
                          <img src="https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=80&q=80" alt="" />
                          <div>
                            <p>1:1 Reiki Session</p>
                            <span>$89 · 10 clients</span>
                          </div>
                          <b>Published</b>
                        </div>
                      </div>

                      <button class="hero-phone__cta" type="button">+ Create new deal</button>
                    </div>
                  </div>
                </div>

                <div class="hero-wallet-stack">
                  <BaseGlassCard class="hero-wallet-card" padding="sm" radius="md">
                    <p class="hero-wallet-card__brand">OpenMat</p>
                    <p class="hero-wallet-card__title">Breathwork Journey</p>
                    <p class="hero-wallet-card__meta">with Marla · Fri 7:00 PM</p>
                  </BaseGlassCard>

                  <div class="hero-nfc">
                    <div class="hero-nfc__icon">◉</div>
                    <p>Hold near reader</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </AppContainer>
    </section>

    <section class="logos-section">
      <AppContainer>
        <BaseGlassCard class="logos-strip" padding="sm" radius="md">
          <p class="logos-strip__label">Trusted by creators and loved by their clients</p>
          <div class="logos-strip__inner">
            <span>mindbody</span>
            <span>Calendly</span>
            <span>Google Wallet</span>
            <span>Apple Wallet</span>
            <span>stripe</span>
          </div>
        </BaseGlassCard>
      </AppContainer>
    </section>

    <section class="steps-section">
      <AppContainer>
        <BaseGlassCard class="steps-shell" padding="md" radius="md">
          <p class="steps-kicker">How it works</p>
          <h2 class="steps-title">From create to redeem in 5 simple steps</h2>

          <div class="steps-scroll">
            <div class="steps-grid">
              <template v-for="(step, index) in steps" :key="step.title">
                <div class="step-card">
                  <div class="step-icon-wrap">{{ step.icon }}</div>
                  <p class="step-number">Step {{ index + 1 }}</p>
                  <p class="step-title">{{ step.title }}</p>
                  <p class="step-desc">{{ step.desc }}</p>
                </div>
                <span v-if="index < steps.length - 1" class="step-arrow">→</span>
              </template>
            </div>
          </div>
        </BaseGlassCard>
      </AppContainer>
    </section>

    <section class="commerce-section">
      <AppContainer>
        <div class="commerce-grid">
          <BaseGlassCard class="commerce-panel" padding="sm" radius="md">
            <p class="commerce-label">Public Deal Page</p>
            <img
              class="deal-hero-image"
              src="https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=1200&q=80"
              alt="Breathwork session hero"
            />

            <div class="deal-heading-row">
              <div>
                <h3 class="deal-title">Breathwork Journey</h3>
                <p class="deal-host">with Marla</p>
              </div>
              <p class="deal-price">$45</p>
            </div>

            <div class="deal-meta">
              <span>🗓 May 24, 2026 · 7:00 PM</span>
              <span>📍 Los Angeles, CA</span>
            </div>

            <AppButton class="deal-book-btn" variant="primary">Book now</AppButton>

            <div class="deal-about">
              <h4>About this experience</h4>
              <p>A guided breathwork journey to release stress, reset your nervous system, and reconnect.</p>
            </div>
          </BaseGlassCard>

          <BaseGlassCard class="commerce-panel" padding="sm" radius="md">
            <p class="commerce-label">Checkout</p>
            <h3 class="checkout-title">Breathwork Journey</h3>
            <p class="checkout-meta">May 24, 2026 · 7:00 PM</p>

            <div class="checkout-divider"></div>

            <div class="checkout-row">
              <span>1 x General Admission</span>
              <strong>$45.00</strong>
            </div>
            <div class="checkout-row">
              <span>Subtotal</span>
              <strong>$45.00</strong>
            </div>
            <div class="checkout-row">
              <span>Processing fee</span>
              <strong>$2.25</strong>
            </div>

            <div class="checkout-total">
              <span>Total</span>
              <strong>$47.25</strong>
            </div>

            <AppButton class="checkout-pay-btn" variant="primary">Pay $47.25</AppButton>
            <p class="checkout-trust">🔒 Secure checkout by Stripe</p>
          </BaseGlassCard>

          <BaseGlassCard class="commerce-panel wallet-panel" padding="sm" radius="md">
            <p class="commerce-label">Wallet Pass Preview</p>

            <div class="wallet-ambient"></div>
            <div class="wallet-phone">
              <div class="wallet-pass">
                <p class="wallet-brand">OpenMat</p>
                <h3>Breathwork Journey</h3>
                <p class="wallet-meta">with Marla</p>
                <p class="wallet-meta">May 24, 2026 at 7:00 PM</p>
                <p class="wallet-meta">Order 4061-12345</p>
                <div class="wallet-qr">▦</div>
              </div>
              <p class="wallet-nfc">⌁ Hold near reader</p>
            </div>
          </BaseGlassCard>
        </div>
      </AppContainer>
    </section>

    <section class="mobile-system-section">
      <AppContainer>
        <p class="mobile-system-kicker">Mobile app previews</p>
        <h2 class="mobile-system-title">Operator app + wallet-native redemption flow</h2>

        <div class="mobile-showcase-wrap">
          <div class="mobile-phone-grid">
          <MobileDeviceShell active-tab="home">
            <div class="iphone-screen">
                <div class="screen-top">
                  <h3>Home</h3>
                  <div class="screen-actions">
                    <button type="button">◌</button>
                    <button type="button">◍</button>
                  </div>
                </div>

                <div class="mobile-featured">
                  <p>Breathwork Journey</p>
                  <span>Today · 7:00 PM · 6 seats left</span>
                </div>

                <div class="mobile-section">
                  <p class="mobile-section__label">Upcoming</p>
                  <div class="mobile-deal-item">
                    <img src="https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=80&q=80" alt="" />
                    <div>
                      <p>Morning Flow</p>
                      <span>Tomorrow · 8:00 AM</span>
                    </div>
                  </div>
                  <div class="mobile-deal-item">
                    <img src="https://images.unsplash.com/photo-1593811167562-9cef47bfc4d7?auto=format&fit=crop&w=80&q=80" alt="" />
                    <div>
                      <p>Sound Bath</p>
                      <span>May 31 · 6:30 PM</span>
                    </div>
                  </div>
                </div>

                <div class="mobile-section">
                  <p class="mobile-section__label">Expiring soon</p>
                  <div class="expiring-chip">3 wallet passes expiring this week</div>
                </div>
            </div>
          </MobileDeviceShell>

          <MobileDeviceShell active-tab="deals">
            <div class="iphone-screen">
                <div class="screen-top">
                  <h3>Deals</h3>
                  <button class="plus-btn" type="button">＋</button>
                </div>

                <div class="deal-list">
                  <div class="deal-row">
                    <img src="https://images.unsplash.com/photo-1488426862026-3ee34a7d66df?auto=format&fit=crop&w=80&q=80" alt="" />
                    <div>
                      <p>Morning Flow</p>
                      <span>$55 · Yoga Class</span>
                    </div>
                    <b class="pill pill--green">Published</b>
                  </div>
                  <div class="deal-row">
                    <img src="https://images.unsplash.com/photo-1593811167562-9cef47bfc4d7?auto=format&fit=crop&w=80&q=80" alt="" />
                    <div>
                      <p>Sound Bath</p>
                      <span>$49 · Shared healing</span>
                    </div>
                    <b class="pill pill--gray">Draft</b>
                  </div>
                  <div class="deal-row">
                    <img src="https://images.unsplash.com/photo-1531746020798-e6953c6e8e04?auto=format&fit=crop&w=80&q=80" alt="" />
                    <div>
                      <p>1:1 Reiki Session</p>
                      <span>$89 · 10 clients</span>
                    </div>
                    <b class="pill pill--red">Sold out</b>
                  </div>
                </div>
            </div>
          </MobileDeviceShell>

          <MobileDeviceShell active-tab="wallet">
            <div class="iphone-screen wallet-screen">
                <div class="wallet-pass-mobile">
                  <p>OpenMat</p>
                  <h4>Breathwork Journey</h4>
                  <span>with Marla</span>
                  <span>May 24, 2026 at 7:00 PM</span>
                  <span>Order 4061-12345</span>
                  <div class="wallet-qr-mobile">▦</div>
                </div>
                <div class="wallet-ripple"></div>
                <p class="wallet-reader-hint">⌁ Hold near reader</p>
            </div>
          </MobileDeviceShell>

          <MobileDeviceShell active-tab="redeem">
            <div class="iphone-screen redeem-screen">
                <h3>Scan or tap pass</h3>
                <div class="scan-frame">
                  <span></span><span></span><span></span><span></span>
                </div>
                <p>Point camera at QR code or use NFC.</p>
            </div>
          </MobileDeviceShell>

          <MobileDeviceShell active-tab="profile">
            <div class="iphone-screen">
                <div class="profile-top">
                  <img v-if="showProfileAvatar" src="https://images.unsplash.com/photo-1542204625-de293a5df31c?auto=format&fit=crop&w=120&q=80" alt="Marla profile" @error="showProfileAvatar = false" />
                  <div v-else class="profile-fallback-avatar">MB</div>
                  <div>
                    <p>Marla B.</p>
                    <span>View profile</span>
                  </div>
                </div>

                <div class="profile-list">
                  <div class="profile-row"><p>Payouts</p><span>›</span></div>
                  <div class="profile-row"><p>Offerings</p><span>›</span></div>
                  <div class="profile-row"><p>Settings</p><span>›</span></div>
                  <div class="profile-row"><p>Connected accounts</p><span>›</span></div>
              </div>
            </div>
          </MobileDeviceShell>
          </div>
        </div>
      </AppContainer>
    </section>

    <AppSection class="pt-0 pb-16 md:pb-20 lg:pb-24">
      <AppContainer>
        <p class="landing-kicker text-center">Built for wellness creators</p>
        <h2 class="categories-title text-center">Empowering every kind of practice</h2>

        <div class="category-grid">
          <article v-for="card in categories" :key="card.title" class="category-card">
            <img :src="card.image" :alt="card.title" class="category-card__image" loading="lazy" />
            <div class="category-card__body">
              <p class="category-card__title">{{ card.title }}</p>
              <p class="category-card__meta">{{ card.meta }}</p>
            </div>
          </article>
        </div>
      </AppContainer>
    </AppSection>
  </div>
</template>

<script setup lang="ts">
import { ref } from "vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppContainer from "../design-system/primitives/AppContainer.vue";
import AppSection from "../design-system/primitives/AppSection.vue";
import BaseGlassCard from "../design-system/primitives/BaseGlassCard.vue";
import GradientOrb from "../design-system/primitives/GradientOrb.vue";
import MobileDeviceShell from "../design-system/primitives/MobileDeviceShell.vue";

const showProfileAvatar = ref(true);
const drawerOpen = ref(false);

const steps = [
  { icon: "✦", title: "Create", desc: "Craft your offer in under 2 minutes." },
  { icon: "↗", title: "Share", desc: "Post your profile link anywhere clients browse." },
  { icon: "◉", title: "Checkout", desc: "Accept secure payments with Stripe." },
  { icon: "▣", title: "Save", desc: "Customers save the pass to Apple Wallet." },
  { icon: "⌁", title: "Redeem", desc: "Scan or mark as redeemed in person." }
];

const categories = [
  {
    title: "Therapists",
    meta: "Private sessions",
    image: "https://images.unsplash.com/photo-1519823551278-64ac92734fb1?auto=format&fit=crop&w=900&q=80"
  },
  {
    title: "Yoga Instructors",
    meta: "Classes & events",
    image: "https://images.unsplash.com/photo-1506126613408-eca07ce68773?auto=format&fit=crop&w=900&q=80"
  },
  {
    title: "Breathwork Coaches",
    meta: "Journeys & workshops",
    image: "https://images.unsplash.com/photo-1593811167562-9cef47bfc4d7?auto=format&fit=crop&w=900&q=80"
  },
  {
    title: "Wellness Centers",
    meta: "Memberships & passes",
    image: "https://images.unsplash.com/photo-1552693673-1bf958298935?auto=format&fit=crop&w=900&q=80"
  },
  {
    title: "Holistic Practitioners",
    meta: "Treatments & more",
    image: "https://images.unsplash.com/photo-1524863479829-916d8e77f114?auto=format&fit=crop&w=900&q=80"
  }
];
</script>

<style scoped>
.landing-view {
  position: relative;
  overflow-x: clip;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
}

.brand__icon {
  display: grid;
  width: 18px;
  height: 18px;
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

.nav-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.mobile-menu-btn {
  width: 44px;
  height: 44px;
  border: 0;
  border-radius: 14px;
  align-items: center;
  justify-content: center;
  font-size: 22px;
  color: rgba(255, 255, 255, 0.88);
  background: rgba(255, 255, 255, 0.04);
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.08);
}

.mobile-drawer-overlay {
  position: fixed;
  inset: 0;
  z-index: 45;
  background: rgba(2, 5, 12, 0.48);
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
  z-index: 46;
  width: 280px;
  height: 100dvh;
  background: rgba(7, 14, 28, 0.97);
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
  gap: 22px;
}

.mobile-drawer__nav a {
  color: var(--text-primary);
  text-decoration: none;
  font-size: 16px;
}

.hero-section {
  padding-top: 48px;
  padding-bottom: 72px;
}

.hero-shell {
  border-radius: 36px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(8, 14, 26, 0.52);
  backdrop-filter: blur(18px);
  box-shadow: inset 0 0 80px rgba(86, 133, 255, 0.07);
}

.hero-grid {
  min-height: 676px;
  display: grid;
  align-items: center;
  gap: 64px;
  padding: 48px;
}

.hero-copy {
  max-width: 720px;
}

.hero-kicker {
  margin: 0;
  color: var(--accent);
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  display: inline-flex;
  align-items: center;
  height: 28px;
  padding-inline: 12px;
  border-radius: 999px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(255, 255, 255, 0.03);
}

.hero-title {
  margin: 20px 0 0;
  max-width: 720px;
  font-size: clamp(64px, 5.2vw, 78px);
  font-weight: 800;
  line-height: 0.92;
  letter-spacing: -0.04em;
}

.hero-title__accent {
  background: linear-gradient(115deg, #f4cc92, #ab8bf5);
  -webkit-background-clip: text;
  background-clip: text;
  color: transparent;
  font-style: italic;
}

.hero-subcopy {
  margin: 28px 0 0;
  max-width: 520px;
  font-size: 22px;
  line-height: 1.6;
  color: rgba(255, 255, 255, 0.78);
}

.hero-cta-row {
  margin-top: 36px;
  display: flex;
  flex-wrap: wrap;
  gap: 18px;
  margin-bottom: 24px;
}

.hero-cta-btn {
  min-height: 60px;
  padding-inline: 34px;
  border-radius: 999px;
  font-weight: 600;
}

.hero-trust-row {
  margin-top: 0;
  display: flex;
  align-items: center;
  gap: 18px;
  flex-wrap: nowrap;
}

.hero-avatars {
  display: flex;
  font-size: 0;
  margin-right: 24px;
}

.hero-avatar {
  display: block;
  width: 42px;
  height: 42px;
  overflow: hidden;
  border-radius: 999px;
  object-fit: cover;
  border: 2px solid rgba(7, 12, 22, 0.9);
}

.hero-avatar + .hero-avatar {
  margin-left: -14px;
}

.hero-rating,
.hero-stars,
.hero-score {
  margin: 0;
  font-size: 16px;
}

.hero-rating {
  color: rgba(255, 255, 255, 0.72);
}

.hero-stars-group {
  display: flex;
  align-items: center;
  gap: 10px;
  white-space: nowrap;
}

.hero-stars {
  color: #f4c97d;
  letter-spacing: 0.1em;
}

.hero-score {
  font-weight: 700;
}

.hero-media {
  position: relative;
  min-height: 660px;
  width: 100%;
  display: flex;
  justify-content: center;
}

.hero-visual-grid {
  width: 100%;
  height: 100%;
  display: grid;
  grid-template-columns: minmax(360px, 1fr) minmax(220px, 0.7fr);
  align-items: center;
  column-gap: 12px;
}

.hero-phone-wrap {
  display: flex;
  justify-content: center;
  transform: translateX(-40px);
}

.hero-left-blue-ambient {
  position: absolute;
  left: -120px;
  top: 186px;
  width: 360px;
  height: 280px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(52, 103, 255, 0.16), transparent 72%);
  filter: blur(128px);
}

.hero-violet-ambient {
  position: absolute;
  inset: 102px -24px 128px 6px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(126, 58, 242, 0.16), transparent 74%);
  filter: blur(144px);
}

.hero-arc-glow {
  position: absolute;
  left: -18px;
  top: 248px;
  width: 372px;
  height: 138px;
  border-radius: 999px;
  background: radial-gradient(65% 80% at 50% 50%, rgba(132, 96, 247, 0.32), rgba(132, 96, 247, 0));
  filter: blur(32px);
}

.hero-hotspot {
  position: absolute;
  right: 8px;
  top: 210px;
  width: 180px;
  height: 180px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(244, 201, 125, 0.18), transparent 74%);
  filter: blur(140px);
}

.hero-phone {
  position: relative;
  width: 332px;
  height: 670px;
  border-radius: 44px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: linear-gradient(180deg, #101625 0%, #0a1220 100%);
  box-shadow: 0 0 60px rgba(0, 0, 0, 0.6), inset 0 1px 0 rgba(255, 255, 255, 0.12);
  overflow: hidden;
}

.hero-phone::before {
  content: "";
  position: absolute;
  inset: 2px;
  border-radius: 42px;
  box-shadow: inset 0 0 0 2px rgba(145, 159, 193, 0.22);
}

.hero-phone__island {
  position: absolute;
  left: 50%;
  top: 12px;
  transform: translateX(-50%);
  width: 122px;
  height: 18px;
  border-radius: 999px;
  background: #0a0f1d;
}

.hero-phone__content {
  position: absolute;
  inset: 40px 14px 14px;
  border-radius: 26px;
  padding: 16px;
  background: linear-gradient(170deg, rgba(17, 24, 40, 0.94), rgba(8, 14, 25, 0.94));
}

.hero-phone__hello {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
}

.hero-phone__muted,
.hero-phone__today {
  margin: 8px 0 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.68);
}

.hero-phone__upcoming {
  margin-top: 12px;
  border-radius: 14px;
  padding: 12px;
  background: linear-gradient(115deg, rgba(120, 99, 243, 0.38), rgba(244, 201, 125, 0.28));
}

.hero-phone__upcoming-title {
  margin: 0;
  font-weight: 600;
}

.hero-phone__upcoming-meta {
  margin: 4px 0 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.74);
}

.hero-phone__section-title {
  margin: 12px 0 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.7);
}

.hero-phone__deal-list {
  display: grid;
  gap: 8px;
}

.hero-phone__deal-row {
  display: grid;
  grid-template-columns: 32px 1fr auto;
  gap: 8px;
  align-items: center;
  border-radius: 10px;
  padding: 8px;
  background: rgba(255, 255, 255, 0.03);
}

.hero-phone__deal-row img {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  object-fit: cover;
}

.hero-phone__deal-row p {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
}

.hero-phone__deal-row span {
  display: block;
  margin-top: 2px;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.62);
}

.hero-phone__deal-row b,
.hero-phone__deal-row i {
  font-size: 10px;
  font-style: normal;
  border-radius: 999px;
  padding: 4px 8px;
}

.hero-phone__deal-row b {
  background: rgba(121, 226, 154, 0.2);
  color: #7ce7a2;
}

.hero-phone__deal-row i {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.74);
}

.hero-phone__cta {
  margin-top: 14px;
  width: 100%;
  height: 42px;
  border: 0;
  border-radius: 12px;
  background: linear-gradient(165deg, #f8da9f 0%, #e0b26c 44%, #c88d43 100%);
  color: #1a1308;
  font-size: 14px;
  font-weight: 700;
}

.hero-wallet-stack {
  grid-column: 2;
  grid-row: 1;
  justify-self: end;
  align-self: start;
  margin-top: 112px;
  margin-right: 24px;
  display: grid;
  gap: 14px;
}

.hero-wallet-card {
  position: relative;
  width: 318px;
  padding: 24px 28px !important;
  border-radius: 28px !important;
  transform: none;
  background: linear-gradient(120deg, rgba(244, 201, 125, 0.4), rgba(126, 58, 242, 0.46)) !important;
  box-shadow: 0 20px 60px rgba(124, 58, 237, 0.28);
}

.hero-wallet-card__brand {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.84);
}

.hero-wallet-card__title {
  margin: 10px 0 0;
  font-size: 34px;
  font-weight: 700;
  line-height: 1;
}

.hero-wallet-card__meta {
  margin: 10px 0 0;
  color: rgba(255, 255, 255, 0.8);
  font-size: 13px;
}

.hero-nfc {
  position: relative;
  justify-self: start;
  display: grid;
  justify-items: center;
  gap: 6px;
  width: 164px;
  padding: 12px;
  border-radius: 14px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(11, 18, 30, 0.46);
  backdrop-filter: blur(14px);
}

.hero-nfc__icon {
  width: 38px;
  height: 38px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  color: #71b6ff;
  border: 1px solid rgba(113, 182, 255, 0.45);
  background: rgba(16, 28, 46, 0.72);
  box-shadow: 0 0 26px rgba(113, 182, 255, 0.26);
}

.hero-nfc p {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.6);
}

.logos-section {
  margin-top: 32px;
  margin-bottom: 40px;
  padding-bottom: 0;
}

.logos-strip {
  max-width: 1400px;
  min-height: 118px;
  height: auto;
  margin-inline: auto;
  display: grid;
  align-items: center;
  padding: 32px 40px;
  border-radius: 28px !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.01)), rgba(14, 22, 36, 0.48) !important;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
}

.logos-strip__label {
  margin: 0 0 18px;
  text-align: center;
  text-transform: uppercase;
  letter-spacing: 0.22em;
  font-size: 11px;
  color: rgba(255, 255, 255, 0.58);
  font-weight: 500;
}

.logos-strip__inner {
  padding-top: 12px;
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
  text-align: center;
  align-items: center;
}

.logos-strip__inner span {
  font-size: 28px;
  letter-spacing: -0.02em;
  opacity: 0.68;
  transition: opacity 180ms ease;
}

.logos-strip__inner span:hover {
  opacity: 1;
}

.steps-section {
  margin-top: 40px;
  padding-bottom: 40px;
}

.steps-shell {
  padding: 40px 48px 40px !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.01)), rgba(13, 20, 34, 0.5) !important;
}

.steps-kicker {
  margin: 0 0 18px;
  text-align: center;
  font-size: 12px;
  letter-spacing: 0.28em;
  text-transform: uppercase;
  color: var(--accent);
}

.steps-title {
  margin: 10px 0 42px;
  text-align: center;
  font-size: clamp(32px, 3.4vw, 44px);
  font-weight: 700;
}

.steps-grid {
  margin-top: 0;
  display: grid;
  gap: 24px;
  width: max-content;
  min-width: 100%;
}

.steps-scroll {
  overflow-x: auto;
  overflow-y: hidden;
  scrollbar-width: thin;
  scrollbar-color: rgba(255, 255, 255, 0.18) transparent;
  padding-bottom: 4px;
}

.step-card {
  position: relative;
  min-width: 210px;
  min-height: 220px;
  padding: 30px 26px 28px;
  border-radius: 20px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.03), rgba(255, 255, 255, 0.01)), linear-gradient(160deg, rgba(13, 18, 30, 0.52), rgba(12, 18, 29, 0.42));
  box-shadow: inset 0 0 0 1px rgba(255, 255, 255, 0.04);
  transition: transform 180ms ease;
}

.step-card:hover {
  transform: translateY(-2px);
}

.step-icon-wrap {
  width: 56px;
  height: 56px;
  border-radius: 18px;
  margin-bottom: 26px;
  border: 1px solid rgba(255, 255, 255, 0.14);
  background: rgba(255, 255, 255, 0.03);
  display: grid;
  place-items: center;
  color: var(--accent);
}

.step-number {
  margin: 0;
  color: var(--accent);
  font-size: 11px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.step-title {
  margin: 20px 0 0;
  font-size: 28px;
  font-weight: 600;
}

.step-desc {
  margin: 12px 0 0;
  color: rgba(255, 255, 255, 0.62);
  font-size: 16px;
  line-height: 1.7;
}

.step-arrow {
  display: none;
}

.commerce-section {
  padding-top: 72px;
  padding-bottom: 56px;
}

.commerce-grid {
  margin: 0 auto;
  max-width: 1380px;
  display: grid;
  gap: 24px;
}

.commerce-panel {
  border-radius: 28px !important;
  border: 1px solid rgba(255, 255, 255, 0.08) !important;
  padding: 22px !important;
  background: linear-gradient(180deg, rgba(10, 14, 28, 0.92), rgba(6, 10, 24, 0.84)) !important;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.28) !important;
  transition: transform 220ms ease, box-shadow 220ms ease;
}

.commerce-panel:hover {
  transform: translateY(-2px);
  box-shadow: 0 24px 74px rgba(0, 0, 0, 0.34) !important;
}

.commerce-label {
  margin: 0 0 18px;
  font-size: 11px;
  letter-spacing: 0.24em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.62);
}

.deal-hero-image {
  width: 100%;
  height: 220px;
  object-fit: cover;
  border-radius: 22px;
  margin-bottom: 22px;
}

.deal-heading-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.deal-title {
  margin: 0;
  font-size: 32px;
  font-weight: 700;
  line-height: 1.08;
}

.deal-host {
  margin: 6px 0 0;
  color: rgba(255, 255, 255, 0.68);
}

.deal-price {
  margin: 2px 0 0;
  font-size: 36px;
  font-weight: 700;
  color: #f4d7a7;
}

.deal-meta {
  margin-top: 18px;
  display: grid;
  gap: 14px;
  color: rgba(255, 255, 255, 0.66);
  font-size: 13px;
}

.deal-book-btn {
  margin-top: 24px;
  min-height: 52px;
  border-radius: 16px;
  box-shadow: 0 0 30px rgba(240, 190, 100, 0.22);
}

.deal-about h4 {
  margin: 24px 0 0;
  font-size: 18px;
  font-weight: 600;
}

.deal-about p {
  margin: 10px 0 0;
  font-size: 15px;
  line-height: 1.7;
  color: rgba(255, 255, 255, 0.72);
}

.checkout-title {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.checkout-meta {
  margin: 8px 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.64);
}

.checkout-divider {
  margin-top: 18px;
  height: 1px;
  background: rgba(255, 255, 255, 0.05);
}

.checkout-row {
  padding: 12px 0;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.checkout-row span {
  color: rgba(255, 255, 255, 0.78);
}

.checkout-row strong {
  font-weight: 600;
}

.checkout-total {
  margin-top: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkout-total span {
  color: rgba(255, 255, 255, 0.8);
}

.checkout-total strong {
  font-size: 24px;
  font-weight: 700;
}

.checkout-pay-btn {
  margin-top: 24px;
  min-height: 54px;
  border-radius: 16px;
}

.checkout-trust {
  margin: 18px 0 0;
  color: rgba(255, 255, 255, 0.58);
  font-size: 12px;
  text-align: center;
}

.wallet-panel {
  position: relative;
  overflow: hidden;
}

.wallet-ambient {
  position: absolute;
  inset: 60px 20px auto;
  height: 260px;
  border-radius: 999px;
  background: radial-gradient(circle, rgba(155, 92, 255, 0.22), rgba(240, 190, 100, 0.16), transparent 72%);
  filter: blur(80px);
  pointer-events: none;
}

.wallet-phone {
  position: relative;
  margin: 0 auto;
  width: min(310px, 100%);
  border-radius: 36px;
  padding: 12px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: linear-gradient(180deg, #101726, #0a1220);
  box-shadow: 0 24px 70px rgba(0, 0, 0, 0.36), inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.wallet-pass {
  border-radius: 24px;
  padding: 18px;
  background: linear-gradient(135deg, #f0be64, #9b5cff, #111827);
}

.wallet-brand {
  margin: 0;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.88);
}

.wallet-pass h3 {
  margin: 16px 0 0;
  font-size: 30px;
  line-height: 1.05;
}

.wallet-meta {
  margin: 8px 0 0;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.82);
}

.wallet-qr {
  width: 120px;
  height: 120px;
  margin: 18px auto 0;
  border-radius: 12px;
  background: #ffffff;
  color: #0b1020;
  display: grid;
  place-items: center;
  font-size: 44px;
  padding: 12px;
}

.wallet-nfc {
  margin: 14px 0 4px;
  text-align: center;
  font-size: 14px;
  color: rgba(255, 255, 255, 0.72);
}

.mobile-system-section {
  --mobile-bg: #050816;
  --mobile-surface: rgba(255, 255, 255, 0.03);
  --mobile-gold: #f0be64;
  --mobile-purple: #b36cff;
  --mobile-text: #f8fafc;
  --mobile-muted: rgba(255, 255, 255, 0.68);
  padding-top: 40px;
  padding-bottom: 56px;
}

.mobile-system-kicker {
  margin: 0;
  text-align: center;
  font-size: 11px;
  letter-spacing: 0.18em;
  text-transform: uppercase;
  color: rgba(255, 255, 255, 0.62);
}

.mobile-system-title {
  margin: 14px 0 0;
  text-align: center;
  font-size: clamp(28px, 3vw, 40px);
  font-weight: 700;
}

.mobile-showcase-wrap {
  margin: 40px auto 0;
  max-width: 1600px;
  padding-inline: 40px;
}

.mobile-phone-grid {
  display: grid;
  gap: 40px;
}

.iphone-screen {
  color: var(--mobile-text);
  width: 100%;
  max-width: 100%;
}

.screen-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.screen-top h3 {
  margin: 0;
  font-size: 28px;
  font-weight: 700;
  line-height: 1;
}

.screen-actions {
  display: flex;
  gap: 8px;
}

.screen-actions button,
.plus-btn {
  width: 34px;
  height: 34px;
  border: 0;
  border-radius: 12px;
  color: rgba(255, 255, 255, 0.8);
  background: var(--mobile-surface);
}

.mobile-featured {
  margin-top: 16px;
  border-radius: 16px;
  padding: 16px;
  background: linear-gradient(145deg, rgba(255, 255, 255, 0.08), rgba(255, 255, 255, 0.02));
}

.mobile-featured p {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.mobile-featured span {
  display: block;
  margin-top: 8px;
  font-size: 13px;
  color: var(--mobile-muted);
}

.mobile-section {
  margin-top: 28px;
}

.mobile-section__label {
  margin: 0 0 14px;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.16em;
  color: var(--mobile-muted);
}

.mobile-deal-item,
.deal-row {
  padding: 14px;
  border-radius: 18px;
  background: var(--mobile-surface);
  display: flex;
  align-items: center;
  gap: 12px;
}

.mobile-deal-item + .mobile-deal-item,
.deal-row + .deal-row {
  margin-top: 14px;
}

.mobile-deal-item img,
.deal-row img {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  object-fit: cover;
}

.mobile-deal-item p,
.deal-row p {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.mobile-deal-item span,
.deal-row span {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: var(--mobile-muted);
}

.expiring-chip {
  border-radius: 14px;
  padding: 12px;
  background: linear-gradient(145deg, rgba(240, 190, 100, 0.24), rgba(240, 190, 100, 0.08));
  color: #f8ddb0;
  font-size: 13px;
}

.deal-list {
  margin-top: 20px;
}

.deal-row {
  display: grid;
  grid-template-columns: 56px minmax(0, 1fr) auto;
  align-items: center;
  column-gap: 12px;
}

.pill {
  font-size: 11px;
  border-radius: 999px;
  padding: 6px 10px;
  font-weight: 600;
  white-space: nowrap;
}

.pill--green {
  background: rgba(106, 224, 147, 0.2);
  color: #78e49d;
}

.pill--gray {
  background: rgba(255, 255, 255, 0.08);
  color: rgba(255, 255, 255, 0.72);
}

.pill--red {
  background: rgba(240, 128, 96, 0.2);
  color: #f0a687;
}

.wallet-screen {
  position: relative;
  overflow: hidden;
}

.wallet-pass-mobile {
  border-radius: 24px;
  padding: 18px;
  background: linear-gradient(135deg, #f0be64, #9b5cff, #111827);
  max-width: 100%;
}

.wallet-pass-mobile p {
  margin: 0;
  font-size: 12px;
}

.wallet-pass-mobile h4 {
  margin: 14px 0 0;
  font-size: 28px;
  line-height: 1.08;
  word-break: break-word;
}

.wallet-pass-mobile span {
  display: block;
  margin-top: 8px;
  font-size: 12px;
  color: rgba(255, 255, 255, 0.82);
  max-width: 100%;
}

.wallet-qr-mobile {
  width: 120px;
  height: 120px;
  margin: 16px auto 0;
  border-radius: 12px;
  background: #fff;
  color: #0f1726;
  display: grid;
  place-items: center;
  font-size: 42px;
  padding: 12px;
}

.wallet-ripple {
  margin: 20px auto 0;
  width: 70px;
  height: 70px;
  border-radius: 999px;
  border: 2px solid rgba(114, 182, 255, 0.55);
  box-shadow: 0 0 24px rgba(114, 182, 255, 0.3);
}

.wallet-reader-hint {
  margin: 12px 0 0;
  text-align: center;
  font-size: 13px;
  color: rgba(255, 255, 255, 0.72);
}

.redeem-screen {
  display: grid;
  justify-items: center;
  align-content: space-between;
  min-height: 100%;
  gap: 20px;
}

.redeem-screen h3 {
  margin: 0;
  font-size: 24px;
  text-align: center;
}

.redeem-screen p {
  margin: 0;
  font-size: 13px;
  color: var(--mobile-muted);
  text-align: center;
}

.scan-frame {
  width: 220px;
  height: 220px;
  border-radius: 20px;
  position: relative;
  background: rgba(0, 0, 0, 0.2);
  margin: 0 auto;
}

.scan-frame span {
  position: absolute;
  width: 34px;
  height: 34px;
  border-color: var(--mobile-gold);
  border-style: solid;
}

.scan-frame span:nth-child(1) {
  top: 0;
  left: 0;
  border-width: 3px 0 0 3px;
  border-radius: 14px 0 0 0;
}

.scan-frame span:nth-child(2) {
  top: 0;
  right: 0;
  border-width: 3px 3px 0 0;
  border-radius: 0 14px 0 0;
}

.scan-frame span:nth-child(3) {
  bottom: 0;
  left: 0;
  border-width: 0 0 3px 3px;
  border-radius: 0 0 0 14px;
}

.scan-frame span:nth-child(4) {
  bottom: 0;
  right: 0;
  border-width: 0 3px 3px 0;
  border-radius: 0 0 14px 0;
}

.profile-top {
  display: flex;
  align-items: center;
  gap: 12px;
}

.profile-top img {
  width: 56px;
  height: 56px;
  border-radius: 999px;
  object-fit: cover;
}

.profile-fallback-avatar {
  width: 56px;
  height: 56px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-size: 16px;
  font-weight: 700;
  color: #f8fafc;
  background: linear-gradient(145deg, rgba(240, 190, 100, 0.32), rgba(179, 108, 255, 0.2));
}

.profile-top p {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.profile-top span {
  display: block;
  margin-top: 4px;
  font-size: 13px;
  color: var(--mobile-muted);
}

.profile-list {
  margin-top: 24px;
  display: grid;
  gap: 12px;
}

.profile-row {
  padding: 14px;
  border-radius: 16px;
  background: var(--mobile-surface);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.profile-row p {
  margin: 0;
  font-size: 16px;
}

.profile-row span {
  color: rgba(255, 255, 255, 0.6);
}

.landing-kicker {
  margin: 0;
  color: var(--accent);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.18em;
  text-transform: uppercase;
}

.categories-title {
  margin: 10px 0 0;
  font-size: clamp(28px, 3.6vw, 40px);
  font-weight: 700;
}

.category-grid {
  margin-top: 26px;
  display: grid;
  gap: 14px;
  grid-template-columns: repeat(1, minmax(0, 1fr));
}

.category-card {
  overflow: hidden;
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.12);
  background: rgba(11, 19, 32, 0.72);
}

.category-card__image {
  width: 100%;
  height: 140px;
  object-fit: cover;
}

.category-card__body {
  padding: 12px;
}

.category-card__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.category-card__meta {
  margin: 4px 0 0;
  color: rgba(255, 255, 255, 0.68);
  font-size: 13px;
}

@media (min-width: 768px) {
  .mobile-phone-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .commerce-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .logos-strip__inner {
    grid-template-columns: repeat(5, minmax(0, 1fr));
    column-gap: 64px;
  }

  .steps-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .category-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (min-width: 1024px) {
  .mobile-drawer,
  .mobile-drawer-overlay {
    display: none;
  }

  .mobile-menu-btn {
    display: none;
  }

  .mobile-phone-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }

  .mobile-phone-grid > * {
    transform: scale(0.94);
    opacity: 0.92;
  }

  .mobile-phone-grid > *:nth-child(3) {
    transform: scale(1);
    opacity: 1;
  }

  .mobile-phone-grid > *:nth-child(1),
  .mobile-phone-grid > *:nth-child(2) {
    transform: scale(0.94) rotate(-1deg);
  }

  .mobile-phone-grid > *:nth-child(4),
  .mobile-phone-grid > *:nth-child(5) {
    transform: scale(0.94) rotate(1deg);
  }

  .commerce-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .hero-grid {
    min-height: 620px;
    grid-template-columns: minmax(620px, 1fr) minmax(540px, 0.84fr);
    padding-left: 40px;
    padding-right: 40px;
  }

  .hero-phone-wrap {
    transform: translateX(-84px);
  }

  .steps-grid {
    grid-template-columns: minmax(210px, 1fr) 40px minmax(210px, 1fr) 40px minmax(210px, 1fr) 40px minmax(210px, 1fr) 40px minmax(210px, 1fr);
    align-items: center;
  }

  .step-arrow {
    width: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: rgba(244, 201, 125, 0.56);
    opacity: 0.38;
    font-size: 20px;
  }

  .category-grid {
    grid-template-columns: repeat(5, minmax(0, 1fr));
  }
}

@media (min-width: 1440px) {
  .hero-shell {
    width: calc(100% + 96px);
    margin-left: -48px;
    margin-right: -48px;
  }

  .hero-grid {
    padding-left: 40px;
    padding-right: 40px;
  }

  .hero-phone {
    width: 344px;
    height: 688px;
  }

  .hero-wallet-stack {
    margin-right: 36px;
  }

  .hero-wallet-card {
    width: 326px;
  }
}

@media (max-width: 1023px) {
  .landing-header__inner {
    padding-left: 16px;
    padding-right: 16px;
  }

  .nav-actions {
    display: none !important;
  }

  .mobile-system-section {
    padding-top: 48px;
    padding-bottom: 40px;
  }

  .mobile-showcase-wrap {
    max-width: none;
    padding-inline: 0;
    margin-top: 28px;
  }

  .commerce-section {
    padding-top: 48px;
    padding-bottom: 40px;
  }

  .commerce-grid {
    gap: 20px;
  }

  .wallet-phone {
    transform: scale(0.82);
    transform-origin: top center;
    margin-bottom: -34px;
  }

  .hero-section {
    padding-top: 0;
    padding-bottom: 48px;
  }

  .hero-shell {
    border-radius: 0;
    border-left: 0;
    border-right: 0;
  }

  .hero-grid {
    min-height: auto;
    gap: 32px;
    padding: 32px 24px;
  }

  .hero-kicker {
    height: 24px;
    padding-inline: 10px;
    font-size: 11px;
  }

  .hero-copy {
    text-align: center;
    margin-inline: auto;
  }

  .hero-title {
    font-size: 46px;
    line-height: 0.94;
  }

  .hero-subcopy,
  .hero-cta-row,
  .hero-trust-row {
    flex-wrap: wrap;
    justify-content: center;
    margin-left: auto;
    margin-right: auto;
  }

  .hero-media {
    min-height: 760px;
    transform: none;
  }

  .hero-visual-grid {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 16px;
  }

  .hero-phone-wrap {
    transform: none;
  }

  .hero-phone {
    position: relative;
    right: auto;
    top: auto;
    margin: 0 auto;
    width: min(320px, 84vw);
    height: 560px;
    display: block;
  }

  .hero-wallet-stack {
    margin: 0;
    justify-self: center;
    align-self: center;
    align-items: center;
  }

  .hero-wallet-card {
    margin: 0;
    position: relative;
    right: auto;
    top: auto;
    width: min(86vw, 360px);
    transform: none;
  }

  .hero-nfc {
    margin: 0;
    position: relative;
    right: auto;
    bottom: auto;
    justify-self: center;
    width: min(72vw, 220px);
  }

  .logos-strip__inner {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .logos-strip__inner span {
    font-size: 20px;
  }

  .steps-shell {
    padding: 40px 24px 32px !important;
  }

  .steps-grid {
    width: 100%;
    gap: 16px;
  }

  .step-arrow {
    display: none;
  }
}

@media (max-width: 768px) {
  .hero-cta-btn {
    min-height: 52px;
    box-shadow: none;
  }

  .hero-trust-row {
    justify-content: center;
  }

  .mobile-showcase-wrap {
    padding-inline: 0;
  }

  .mobile-phone-grid {
    display: flex;
    gap: 20px;
    overflow-x: auto;
    padding-inline: 20px;
    scroll-snap-type: x mandatory;
    -webkit-overflow-scrolling: touch;
  }

  .mobile-phone-grid > * {
    flex: 0 0 auto;
    scroll-snap-align: center;
    transform: scale(0.92);
    opacity: 0.72;
  }

  .mobile-phone-grid > *:nth-child(3) {
    transform: scale(1);
    opacity: 1;
  }
}
</style>
