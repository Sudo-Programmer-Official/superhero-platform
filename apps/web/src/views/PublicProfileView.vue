<template>
  <section class="public-profile" :style="accentVars">
    <article class="hero" :style="coverStyle">
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="avatar-wrap">
          <img v-if="practitioner?.avatar_url || practitioner?.profile_image" :src="practitioner?.avatar_url || practitioner?.profile_image || ''" alt="Profile" class="avatar" />
          <div v-else class="avatar avatar--fallback">{{ initials }}</div>
        </div>
        <div>
          <p class="eyebrow">Practitioner</p>
          <h1>{{ practitioner?.name || practitionerSlug }}</h1>
          <p class="tagline">{{ practitioner?.tagline || practitioner?.category || "Wellness creator" }}</p>
          <p class="meta">{{ practitioner?.location || "Location not provided" }} · {{ practitioner?.verification_state || "unverified" }}</p>
        </div>
      </div>
      <div class="social-row">
        <a v-for="item in socialItems" :key="item.label" :href="item.url" target="_blank" rel="noopener noreferrer">{{ item.label }}</a>
      </div>
    </article>

    <article class="about card">
      <h2>About</h2>
      <p>{{ practitioner?.bio || "Profile story coming soon." }}</p>
    </article>

    <article class="experiences card">
      <div class="section-head">
        <h2>Upcoming Experiences</h2>
        <AppButton variant="ghost" @click="onCopyProfile">Copy profile URL</AppButton>
      </div>
      <div class="deal-grid">
        <article v-for="deal in deals" :key="deal.id" class="deal-card">
          <img v-if="deal.image" :src="deal.image" alt="Deal cover" class="deal-image" />
          <div v-else class="deal-image deal-image--fallback"></div>
          <div class="deal-body">
            <p class="deal-status">{{ deal.status.toUpperCase() }}</p>
            <h3>{{ deal.title }}</h3>
            <p>{{ deal.location_name }} · {{ formatEventTime(deal.start_at, deal.timezone) }}</p>
            <div class="deal-foot">
              <strong>${{ deal.price }}</strong>
              <AppButton tag="RouterLink" variant="secondary" :to="`/openmat/${practitionerSlug}/${deal.slug}`">View</AppButton>
            </div>
          </div>
        </article>
      </div>
    </article>

    <article class="trust card">
      <h2>Trust & Booking</h2>
      <p>Secure checkout, wallet-enabled entry, and verified practitioner identity workflow.</p>
      <div class="trust-grid">
        <span>Wallet-ready</span>
        <span>Secure checkout</span>
        <span>Mobile passes</span>
        <span>Public profile</span>
      </div>
    </article>

    <article class="testimonials card">
      <h2>Testimonials</h2>
      <p>Reviews module coming soon.</p>
    </article>

  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AppButton from "../design-system/primitives/AppButton.vue";
import { formatLocalDateTime, formatTimezone } from "../domain/deal";
import { fetchPublicPractitioner, listPublicDeals, type DealCardPayload, type PractitionerPublicPayload } from "../services/api";
import { showToast } from "../stores/toast";

const route = useRoute();
const practitionerSlug = String(route.params.practitionerSlug || "");
const deals = ref<DealCardPayload[]>([]);
const practitioner = ref<PractitionerPublicPayload | null>(null);

const initials = computed(() => {
  const parts = (practitioner.value?.name || practitionerSlug || "OpenMat").split(/\s+/).filter(Boolean).slice(0, 2);
  return parts.map((part) => part[0]?.toUpperCase() || "").join("") || "OM";
});

const accentVars = computed(() => ({
  "--profile-accent": practitioner.value?.accent_color || "#f4d8a7"
}));

const coverStyle = computed(() => {
  const cover = practitioner.value?.cover_image_url;
  if (!cover) return {};
  return { backgroundImage: `url(${cover})` };
});

const socialItems = computed(() => {
  const links = practitioner.value?.social_links || {};
  return Object.entries(links)
    .filter(([, value]) => Boolean(value))
    .map(([key, value]) => ({ label: key, url: value as string }));
});

async function load() {
  if (!practitionerSlug) return;
  try {
    practitioner.value = await fetchPublicPractitioner(practitionerSlug);
    deals.value = await listPublicDeals(practitionerSlug);
    document.title = `${practitioner.value.name} · OpenMat`;
  } catch (err) {
    showToast(`Failed to load profile: ${String(err)}`, "error");
  }
}

function profileUrl(): string {
  return `${window.location.origin}/p/${practitionerSlug}`;
}

async function onCopyProfile() {
  try {
    await navigator.clipboard.writeText(profileUrl());
    showToast("Profile link copied", "success");
  } catch {
    showToast("Could not copy profile link", "error");
  }
}

function formatEventTime(value: string, timezone: string): string {
  return `${formatLocalDateTime(value, timezone)} ${formatTimezone(value, timezone)}`;
}

onMounted(load);
</script>

<style scoped>
.public-profile { max-width: 1120px; margin: 0 auto; padding: 24px 20px 48px; display: grid; gap: 20px; }
.hero {
  position: relative;
  border-radius: 28px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,.16);
  background: radial-gradient(120% 140% at 0% 0%, color-mix(in srgb, var(--profile-accent), #0b1425 65%), #081222 72%);
  min-height: 300px;
}
.hero::before { content: ""; position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,.12), rgba(0,0,0,.5)); }
.hero-overlay { position: absolute; inset: 0; backdrop-filter: blur(2px); }
.hero-content { position: relative; z-index: 2; display: grid; grid-template-columns: auto 1fr; gap: 20px; padding: 28px; align-items: center; }
.avatar-wrap { width: 108px; height: 108px; }
.avatar { width: 108px; height: 108px; border-radius: 999px; border: 1px solid rgba(255,255,255,.24); object-fit: cover; }
.avatar--fallback { display: grid; place-items: center; background: linear-gradient(145deg, color-mix(in srgb, var(--profile-accent), #24344f 30%), #0e1c32); color: #fff; font-size: 30px; font-weight: 700; }
.eyebrow { margin: 0; text-transform: uppercase; letter-spacing: .1em; font-size: 12px; color: rgba(255,255,255,.72); }
.hero h1 { margin: 8px 0 0; font-size: clamp(38px, 5vw, 58px); line-height: 1.05; letter-spacing: -0.02em; }
.tagline { margin: 12px 0 0; font-size: 18px; color: rgba(255,255,255,.88); }
.meta { margin: 8px 0 0; font-size: 13px; color: rgba(255,255,255,.74); text-transform: capitalize; }
.social-row { position: relative; z-index: 2; padding: 0 28px 24px; display: flex; flex-wrap: wrap; gap: 10px; }
.social-row a { text-decoration: none; border-radius: 999px; border: 1px solid rgba(255,255,255,.2); color: rgba(255,255,255,.9); padding: 8px 12px; background: rgba(255,255,255,.06); }
.card { border-radius: 22px; border: 1px solid rgba(255,255,255,.12); background: rgba(10,18,32,.72); padding: 24px; }
.card h2 { margin: 0 0 12px; font-size: 28px; letter-spacing: -0.01em; }
.card p { margin: 0; color: rgba(255,255,255,.72); line-height: 1.5; }
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.deal-grid { margin-top: 14px; display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 16px; }
.deal-card { border-radius: 18px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.02); overflow: hidden; }
.deal-image { width: 100%; height: 150px; object-fit: cover; }
.deal-image--fallback { background: linear-gradient(135deg, rgba(38,55,80,.8), rgba(9,16,29,.95)); }
.deal-body { padding: 14px; display: grid; gap: 10px; }
.deal-status { margin: 0; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: color-mix(in srgb, var(--profile-accent), #fff 22%); }
.deal-body h3 { margin: 0; font-size: 22px; line-height: 1.15; }
.deal-body p { margin: 0; font-size: 13px; color: rgba(255,255,255,.64); }
.deal-foot { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.deal-foot strong { font-size: 22px; color: #fff; }
.trust-grid { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 10px; }
.trust-grid span { border-radius: 999px; border: 1px solid rgba(255,255,255,.16); padding: 7px 10px; font-size: 12px; color: rgba(255,255,255,.84); }
@media (max-width: 1023px) {
  .hero-content { grid-template-columns: 1fr; }
  .deal-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 767px) {
  .public-profile { padding: 16px 16px 28px; }
  .deal-grid { grid-template-columns: 1fr; }
}
</style>
