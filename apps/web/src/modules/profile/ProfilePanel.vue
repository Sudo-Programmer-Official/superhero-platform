<template>
  <section class="profile-studio">
    <PaddedSectionCard class="hero-card">
      <div class="hero-main">
        <div class="avatar-wrap">
          <div class="avatar-ring"></div>
          <img v-if="form.avatar_url" :src="form.avatar_url" alt="Avatar" class="avatar" />
          <div v-else class="avatar avatar--fallback">{{ initials }}</div>
        </div>
        <div class="hero-copy">
          <p class="eyebrow">Practitioner Identity</p>
          <h2>{{ form.name || "Your profile" }}</h2>
          <p>{{ form.tagline || "Define your wellness brand identity and public presence." }}</p>
          <div class="hero-meta">
            <span class="badge">{{ verificationLabel }}</span>
            <span>{{ form.location || "Location not provided" }}</span>
            <span>/p/{{ form.slug || "your-slug" }}</span>
          </div>
        </div>
      </div>
      <div class="hero-actions">
        <label class="field">
          <span>Avatar URL</span>
          <AppInput v-model="form.avatar_url" placeholder="https://..." />
        </label>
        <label class="field">
          <span>Cover Image URL</span>
          <AppInput v-model="form.cover_image_url" placeholder="https://..." />
        </label>
      </div>
    </PaddedSectionCard>

    <PaddedSectionCard>
      <div class="section-head">
        <h3>Profile Completion</h3>
        <strong>{{ completion }}% complete</strong>
      </div>
      <div class="progress-track"><div class="progress-fill" :style="{ width: `${completion}%` }"></div></div>
      <p class="helper">Complete bio, social links, branding, and public slug to strengthen trust and discoverability.</p>
    </PaddedSectionCard>

    <PaddedSectionCard>
      <div class="section-head"><h3>Practice Details</h3></div>
      <div class="grid-2">
        <label class="field"><span>Practice Name</span><AppInput v-model="form.name" placeholder="Your practice name" /></label>
        <label class="field"><span>Category</span><AppInput v-model="form.category" placeholder="Breathwork" /></label>
        <label class="field"><span>Specialties (comma separated)</span><AppInput v-model="specialtiesText" placeholder="Sound bath, Yoga, Meditation" /></label>
        <label class="field"><span>Location</span><AppInput v-model="form.location" placeholder="Chicago, IL" /></label>
        <label class="field"><span>Booking Policies</span><AppInput v-model="form.booking_policies" placeholder="24h cancellation policy" /></label>
        <label class="field"><span>Support Email</span><AppInput v-model="form.support_email" placeholder="support@yourstudio.com" /></label>
      </div>
      <label class="field"><span>Tagline</span><AppInput v-model="form.tagline" placeholder="Nervous system reset for founders and creatives" /></label>
    </PaddedSectionCard>

    <PaddedSectionCard>
      <div class="section-head"><h3>Social Links</h3></div>
      <div class="grid-2">
        <label class="field"><span>Instagram</span><AppInput v-model="form.social_links.instagram" placeholder="https://instagram.com/..." /></label>
        <label class="field"><span>TikTok</span><AppInput v-model="form.social_links.tiktok" placeholder="https://tiktok.com/@..." /></label>
        <label class="field"><span>YouTube</span><AppInput v-model="form.social_links.youtube" placeholder="https://youtube.com/..." /></label>
        <label class="field"><span>LinkedIn</span><AppInput v-model="form.social_links.linkedin" placeholder="https://linkedin.com/in/..." /></label>
        <label class="field"><span>Website</span><AppInput v-model="form.website" placeholder="https://yourstudio.com" /></label>
      </div>
    </PaddedSectionCard>

    <PaddedSectionCard>
      <div class="section-head"><h3>Bio / Story</h3></div>
      <label class="field">
        <span>About your practice</span>
        <textarea v-model="form.bio" rows="6" class="textarea" placeholder="Share your story, approach, and values."></textarea>
      </label>
    </PaddedSectionCard>

    <PaddedSectionCard>
      <div class="section-head"><h3>Branding Settings</h3></div>
      <div class="grid-2">
        <label class="field"><span>Accent Color</span><input v-model="form.accent_color" type="color" class="color" /></label>
        <label class="field"><span>Public Slug</span><AppInput v-model="form.slug" placeholder="marla" /></label>
        <label class="field"><span>Logo URL</span><AppInput v-model="form.logo_url" placeholder="https://..." /></label>
        <label class="field"><span>Verification State</span><AppInput v-model="form.verification_state" placeholder="unverified" /></label>
      </div>
    </PaddedSectionCard>

    <PaddedSectionCard>
      <div class="section-head"><h3>Account Status</h3></div>
      <div class="status-grid">
        <p><span>Stripe</span><strong>{{ stripeState }}</strong></p>
        <p><span>Wallet</span><strong>{{ walletState }}</strong></p>
        <p><span>Public Profile</span><strong>{{ publicState }}</strong></p>
        <p><span>Upcoming Deals</span><strong>{{ upcomingDeals }}</strong></p>
      </div>
    </PaddedSectionCard>

    <PaddedSectionCard>
      <div class="quick-actions">
        <AppButton variant="primary" @click="viewPublic">View Public Profile</AppButton>
        <AppButton variant="secondary" @click="shareProfile">Share Profile</AppButton>
        <AppButton variant="ghost" @click="copyPublicUrl">Copy Public URL</AppButton>
        <AppButton tag="RouterLink" to="/dashboard/deals/create" variant="ghost">Create Deal</AppButton>
      </div>
      <div class="save-row">
        <p class="helper">{{ saveState }}</p>
        <AppButton variant="primary" :disabled="saving" @click="saveNow">{{ saving ? "Saving..." : "Save Profile" }}</AppButton>
      </div>
    </PaddedSectionCard>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useRouter } from "vue-router";
import AppButton from "../../design-system/primitives/AppButton.vue";
import AppInput from "../../design-system/primitives/AppInput.vue";
import PaddedSectionCard from "../../design-system/patterns/PaddedSectionCard.vue";
import { listDeals, updatePractitioner, fetchPublicPractitioner, type PractitionerUpdatePayload } from "../../services/api";
import { sessionState } from "../../stores/session";

const router = useRouter();
const saving = ref(false);
const saveState = ref("Not saved yet");
const upcomingDeals = ref(0);
const specialtiesText = ref("");
let saveTimer: number | null = null;

const form = reactive({
  name: "",
  slug: "",
  avatar_url: "",
  cover_image_url: "",
  logo_url: "",
  bio: "",
  category: "",
  tagline: "",
  specialties: [] as string[],
  booking_policies: "",
  website: "",
  support_email: "",
  accent_color: "#f4d8a7",
  verification_state: "unverified",
  location: "",
  social_links: {
    instagram: "",
    tiktok: "",
    youtube: "",
    linkedin: ""
  }
});

const initials = computed(() => {
  const parts = (form.name || "OpenMat").split(/\s+/).filter(Boolean).slice(0, 2);
  return parts.map((part) => part[0]?.toUpperCase() || "").join("") || "OM";
});

const verificationLabel = computed(() => (form.verification_state || "unverified").replaceAll("_", " "));
const stripeState = computed(() => (sessionState.me?.role === "practitioner" ? "Connected" : "Pending"));
const walletState = computed(() => "Enabled");
const publicState = computed(() => (form.slug ? "Live" : "Draft"));

const completion = computed(() => {
  const checks = [
    Boolean(form.name.trim()),
    Boolean(form.bio.trim()),
    Boolean(form.avatar_url.trim()),
    Boolean(form.cover_image_url.trim()),
    Boolean(form.slug.trim()),
    Boolean(form.category.trim()),
    Boolean(form.location.trim()),
    Boolean(form.website.trim()),
    Boolean(form.support_email.trim()),
    Object.values(form.social_links).some((v) => (v || "").trim())
  ];
  const points = checks.filter(Boolean).length;
  return Math.round((points / checks.length) * 100);
});

function publicUrl() {
  return `${window.location.origin}/p/${form.slug || sessionState.me?.practitioner_slug || ""}`;
}

function scheduleAutosave() {
  saveState.value = "Unsaved changes";
  if (saveTimer) window.clearTimeout(saveTimer);
  saveTimer = window.setTimeout(() => {
    void saveNow();
  }, 1500);
}

async function saveNow() {
  if (!sessionState.token || !sessionState.me?.practitioner_id) return;
  saving.value = true;
  saveState.value = "Saving...";
  try {
    const payload: PractitionerUpdatePayload = {
      name: form.name || undefined,
      slug: form.slug || undefined,
      avatar_url: form.avatar_url || null,
      cover_image_url: form.cover_image_url || null,
      logo_url: form.logo_url || null,
      bio: form.bio || null,
      category: form.category || null,
      tagline: form.tagline || null,
      specialties: specialtiesText.value.split(",").map((v) => v.trim()).filter(Boolean),
      booking_policies: form.booking_policies || null,
      website: form.website || null,
      support_email: form.support_email || null,
      accent_color: form.accent_color || null,
      verification_state: form.verification_state || null,
      location: form.location || null,
      social_links: {
        instagram: form.social_links.instagram || null,
        tiktok: form.social_links.tiktok || null,
        youtube: form.social_links.youtube || null,
        linkedin: form.social_links.linkedin || null,
        website: form.website || null
      }
    };
    const updated = await updatePractitioner(sessionState.token, sessionState.me.practitioner_id, payload);
    form.slug = updated.slug;
    saveState.value = "Saved";
  } catch (err) {
    saveState.value = `Save failed: ${String(err)}`;
  } finally {
    saving.value = false;
  }
}

async function loadProfile() {
  const slug = sessionState.me?.practitioner_slug;
  if (!slug) return;
  const data = await fetchPublicPractitioner(slug);
  form.name = data.name || "";
  form.slug = data.slug || "";
  form.avatar_url = data.avatar_url || data.profile_image || "";
  form.cover_image_url = data.cover_image_url || "";
  form.logo_url = data.logo_url || "";
  form.bio = data.bio || "";
  form.category = data.category || "";
  form.tagline = data.tagline || "";
  form.specialties = data.specialties || [];
  specialtiesText.value = form.specialties.join(", ");
  form.booking_policies = data.booking_policies || "";
  form.website = data.website || "";
  form.support_email = data.support_email || "";
  form.accent_color = data.accent_color || "#f4d8a7";
  form.verification_state = data.verification_state || "unverified";
  form.location = data.location || "";
  form.social_links.instagram = data.social_links?.instagram || "";
  form.social_links.tiktok = data.social_links?.tiktok || "";
  form.social_links.youtube = data.social_links?.youtube || "";
  form.social_links.linkedin = data.social_links?.linkedin || "";
}

async function loadDealCount() {
  if (!sessionState.token) return;
  const deals = await listDeals(sessionState.token);
  upcomingDeals.value = deals.filter((deal) => deal.status === "published").length;
}

function viewPublic() {
  window.open(publicUrl(), "_blank", "noopener,noreferrer");
}

async function copyPublicUrl() {
  await navigator.clipboard.writeText(publicUrl());
  saveState.value = "Public URL copied";
}

async function shareProfile() {
  const url = publicUrl();
  if (navigator.share) {
    await navigator.share({ title: form.name || "OpenMat profile", url });
  } else {
    await navigator.clipboard.writeText(url);
  }
  saveState.value = "Profile shared";
}

watch(
  () => [
    form.name,
    form.slug,
    form.avatar_url,
    form.cover_image_url,
    form.logo_url,
    form.bio,
    form.category,
    form.tagline,
    specialtiesText.value,
    form.booking_policies,
    form.website,
    form.support_email,
    form.accent_color,
    form.verification_state,
    form.location,
    form.social_links.instagram,
    form.social_links.tiktok,
    form.social_links.youtube,
    form.social_links.linkedin
  ],
  () => scheduleAutosave()
);

onMounted(async () => {
  try {
    await Promise.all([loadProfile(), loadDealCount()]);
    saveState.value = "Ready";
  } catch (err) {
    saveState.value = `Load failed: ${String(err)}`;
  }
});
</script>

<style scoped>
.profile-studio { display: grid; gap: 24px; }
.hero-card { display: grid; gap: 20px; }
.hero-main { display: grid; grid-template-columns: auto 1fr; gap: 20px; align-items: center; }
.avatar-wrap { position: relative; width: 108px; height: 108px; }
.avatar-ring { position: absolute; inset: -6px; border-radius: 999px; background: radial-gradient(circle, rgba(240,190,100,.35), rgba(240,190,100,0)); filter: blur(8px); }
.avatar { position: relative; width: 108px; height: 108px; border-radius: 999px; object-fit: cover; border: 1px solid rgba(255,255,255,.2); }
.avatar--fallback { display: grid; place-items: center; background: linear-gradient(145deg, rgba(244,201,125,.3), rgba(52,68,102,.5)); color: #f4d8a7; font-size: 28px; font-weight: 700; }
.hero-copy .eyebrow { margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: .1em; color: rgba(255,255,255,.62); }
.hero-copy h2 { margin: 8px 0 0; font-size: 38px; line-height: 1.1; letter-spacing: -0.02em; }
.hero-copy p { margin: 10px 0 0; color: rgba(255,255,255,.68); }
.hero-meta { margin-top: 14px; display: flex; flex-wrap: wrap; gap: 10px; font-size: 13px; color: rgba(255,255,255,.72); }
.badge { border-radius: 999px; border: 1px solid rgba(240,190,100,.44); color: #f4d8a7; padding: 4px 9px; text-transform: uppercase; letter-spacing: .08em; font-size: 11px; }
.hero-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.section-head { display: flex; align-items: center; justify-content: space-between; gap: 12px; }
.section-head h3 { margin: 0; font-size: 24px; letter-spacing: -0.01em; }
.section-head strong { color: #f4d8a7; }
.progress-track { height: 10px; border-radius: 999px; background: rgba(255,255,255,.08); overflow: hidden; }
.progress-fill { height: 100%; background: linear-gradient(90deg, rgba(240,190,100,.9), rgba(82,213,139,.92)); }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field { display: grid; gap: 8px; }
.field span { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.62); }
.textarea, .color { width: 100%; border-radius: 14px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,18,30,.62); color: #dbe5f3; padding: 12px; }
.color { min-height: 48px; padding: 6px; }
.helper { margin: 0; color: rgba(255,255,255,.64); font-size: 14px; }
.status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.status-grid p { margin: 0; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 12px; display: grid; gap: 6px; }
.status-grid span { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.58); }
.status-grid strong { font-size: 18px; color: #f1f6ff; }
.quick-actions { display: flex; flex-wrap: wrap; gap: 12px; }
.save-row { margin-top: 16px; display: flex; justify-content: space-between; align-items: center; gap: 12px; }
@media (max-width: 1023px) {
  .hero-main { grid-template-columns: 1fr; }
  .hero-actions, .grid-2, .status-grid { grid-template-columns: 1fr; }
  .save-row { flex-direction: column; align-items: flex-start; }
}
</style>
