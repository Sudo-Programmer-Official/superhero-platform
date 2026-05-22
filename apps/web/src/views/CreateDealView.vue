<template>
  <section class="deal-studio">
    <AppCard class="deal-studio__header">
      <div>
        <p class="eyebrow">Deal Studio</p>
        <h1>Create Deal Workflow</h1>
        <p>Configure, preview, publish, and share in one guided flow.</p>
      </div>
      <div class="deal-studio__steps">
        <button v-for="(label, idx) in steps" :key="label" type="button" class="step-chip" :class="{ 'is-active': studio.step === idx + 1 }" @click="studio.step = idx + 1">
          {{ idx + 1 }}. {{ label }}
        </button>
      </div>
    </AppCard>

    <div class="deal-studio__grid">
      <AppCard class="deal-studio__panel">
        <template v-if="studio.step === 1">
          <h2>Configure</h2>
          <div class="field-grid">
            <div class="field"><label>Title</label><AppInput v-model="studio.form.title" placeholder="Breathwork Journey" /></div>
            <div class="field"><label>Category</label><AppInput v-model="studio.form.category" placeholder="Breathwork" /></div>
            <div class="field"><label>Location</label><AppInput v-model="studio.form.location" placeholder="Los Angeles, CA" /></div>
            <div class="field"><label>Cover image URL</label><AppInput v-model="studio.form.coverImage" placeholder="https://..." /></div>
            <div class="field"><label>Start</label><AppInput v-model="studio.form.startsAt" type="datetime-local" /></div>
            <div class="field"><label>End</label><AppInput v-model="studio.form.endsAt" type="datetime-local" /></div>
            <div class="field">
              <label>Timezone</label>
              <select v-model="studio.form.timezone" class="field-select">
                <option v-for="tz in timezoneOptions" :key="tz" :value="tz">{{ tz }}</option>
              </select>
            </div>
            <div class="field"><label>Seats</label><AppInput v-model="studio.form.seats" type="number" placeholder="20" /></div>
            <div class="field"><label>Pricing (USD)</label><AppInput v-model="studio.form.price" type="number" placeholder="45.00" /></div>
            <div class="field">
              <label>Redemption type</label>
              <select v-model="studio.form.redemptionType" class="field-select"><option value="qr">QR</option><option value="nfc">NFC</option></select>
            </div>
            <div class="field">
              <label>Visibility</label>
              <select v-model="studio.form.visibility" class="field-select"><option value="public">Public</option><option value="private">Private</option></select>
            </div>
          </div>
          <div class="field"><label>Description</label><textarea v-model="studio.form.description" rows="4" class="field-textarea" placeholder="Describe the experience"></textarea></div>
        </template>

        <template v-else-if="studio.step === 2">
          <h2>Preview</h2>
          <p class="muted">Live public card preview and wallet pass preview.</p>
          <div class="preview-row">
            <article class="public-preview">
              <img v-if="studio.form.coverImage" :src="studio.form.coverImage" alt="Cover" />
              <div v-else class="public-preview__img-fallback"></div>
              <h3>{{ studio.form.title || 'Untitled deal' }}</h3>
              <p>{{ studio.form.description || 'Add description to improve conversion.' }}</p>
              <div class="meta">{{ formattedStart }} · {{ studio.form.location || 'Location pending' }}</div>
              <div class="price">${{ studio.form.price || '0.00' }}</div>
            </article>
            <article class="wallet-preview">
              <p class="wallet-brand">OpenMat Pass</p>
              <h4>{{ studio.form.title || 'Untitled deal' }}</h4>
              <p>{{ formattedStart }}</p>
              <p>{{ studio.form.redemptionType.toUpperCase() }} redemption</p>
              <div class="wallet-qr">▦</div>
            </article>
          </div>
        </template>

        <template v-else-if="studio.step === 3">
          <h2>Publish</h2>
          <p class="muted">Create draft first, then publish and generate share assets.</p>
          <div class="publish-actions">
            <AppButton variant="secondary" :disabled="studio.status === 'saving' || studio.status === 'publishing'" @click="onCreateDraft">
              {{ studio.status === 'saving' ? 'Creating draft...' : 'Create draft' }}
            </AppButton>
            <AppButton variant="primary" :disabled="!studio.lastDraftId || studio.status === 'publishing'" @click="onPublish">
              {{ studio.status === 'publishing' ? 'Publishing...' : 'Publish deal' }}
            </AppButton>
          </div>
          <p class="muted">Status: <span class="badge">{{ draftBadge }}</span></p>
        </template>

        <template v-else>
          <h2>Share</h2>
          <p class="muted">Copy link, open public page, or share QR.</p>
          <div class="share-grid">
            <div class="field"><label>Public URL</label><input class="field-readonly" :value="studio.shareUrl" readonly /></div>
            <div class="share-actions">
              <AppButton variant="secondary" :disabled="!studio.shareUrl" @click="copyShare">Copy link</AppButton>
              <AppButton variant="primary" :disabled="!studio.shareUrl" @click="openShare">Open page</AppButton>
            </div>
            <div class="qr-wrap" v-if="studio.qrUrl"><img :src="studio.qrUrl" alt="Share QR" /></div>
            <div class="qr-wrap qr-wrap--empty" v-else>No QR yet. Publish first.</div>
          </div>
        </template>

        <div class="nav-actions">
          <AppButton variant="ghost" :disabled="studio.step === 1" @click="prevDealStudioStep">Back</AppButton>
          <AppButton variant="primary" :disabled="studio.step === 4" @click="nextDealStudioStep">Next</AppButton>
        </div>
      </AppCard>

      <AppCard class="deal-studio__side" muted>
        <h3>Workflow State</h3>
        <ul>
          <li>Loading state: {{ studio.status }}</li>
          <li>Draft: {{ studio.lastDraftId ? 'created' : 'none' }}</li>
          <li>Share ready: {{ studio.shareUrl ? 'yes' : 'no' }}</li>
          <li>Visibility: {{ studio.form.visibility }}</li>
        </ul>
        <AppButton variant="ghost" @click="resetDealStudio">Reset flow</AppButton>
      </AppCard>
    </div>

    <transition name="toast-fade">
      <div v-if="studio.toast" class="toast">{{ studio.toast }}</div>
    </transition>
  </section>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRouter } from "vue-router";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import AppInput from "../design-system/primitives/AppInput.vue";
import { formatLocalDateTime, formatTimezone } from "../domain/deal";
import { createDeal, updateDealStatus } from "../services/api";
import { dealStudioState as studio, nextDealStudioStep, prevDealStudioStep, resetDealStudio, setDealStudioToast } from "../stores/dealStudio";
import { sessionState } from "../stores/session";

const router = useRouter();
const steps = ["Configure", "Preview", "Publish", "Share"];

const formattedStart = computed(() => {
  if (!studio.form.startsAt) return "Date pending";
  const iso = new Date(studio.form.startsAt).toISOString();
  return `${formatLocalDateTime(iso, studio.form.timezone)} ${formatTimezone(iso, studio.form.timezone)}`;
});

const timezoneOptions = [
  Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "Europe/London",
  "Asia/Kolkata",
  "Asia/Tokyo"
].filter((value, index, self) => self.indexOf(value) === index);

const draftBadge = computed(() => {
  if (studio.status === "publishing") return "publishing";
  if (studio.lastDraftId) return "draft ready";
  return "not created";
});

function requireAuthContext() {
  if (!sessionState.token || !sessionState.me?.practitioner_id) {
    throw new Error("Authentication session expired.");
  }
  return {
    token: sessionState.token,
    practitionerId: sessionState.me.practitioner_id
  };
}

async function onCreateDraft() {
  try {
    const auth = requireAuthContext();
    studio.status = "saving";
    const draft = await createDeal(auth.token, {
      practitioner_id: auth.practitionerId,
      title: studio.form.title || "Untitled Deal",
      description: studio.form.description || null,
      location: studio.form.location || "TBD",
      timezone: studio.form.timezone || "UTC",
      image: studio.form.coverImage || null,
      price: studio.form.price || "0.00",
      capacity: Number(studio.form.seats || 0),
      cta_text: "Book now",
      booking_url: null,
      start_time: studio.form.startsAt ? new Date(studio.form.startsAt).toISOString() : new Date().toISOString(),
      end_time: studio.form.endsAt ? new Date(studio.form.endsAt).toISOString() : new Date(Date.now() + 3600_000).toISOString(),
      wallet_enabled: studio.form.redemptionType === "qr"
    });
    studio.lastDraftId = draft.id;
    studio.status = "idle";
    setDealStudioToast("Draft created");
  } catch (err) {
    studio.status = "idle";
    setDealStudioToast(`Draft failed: ${String(err)}`);
  }
}

async function onPublish() {
  if (!studio.lastDraftId) return;
  try {
    const auth = requireAuthContext();
    studio.status = "publishing";
    const published = await updateDealStatus(auth.token, studio.lastDraftId, "published");
    studio.status = "done";
    studio.shareUrl = `${window.location.origin}${published.share_link || `/openmat/${sessionState.me?.practitioner_slug}/${published.slug}`}`;
    studio.qrUrl = `https://api.qrserver.com/v1/create-qr-code/?size=220x220&data=${encodeURIComponent(studio.shareUrl)}`;
    studio.step = 4;
    setDealStudioToast("Deal published and share ready");
  } catch (err) {
    studio.status = "idle";
    setDealStudioToast(`Publish failed: ${String(err)}`);
  }
}

async function copyShare() {
  if (!studio.shareUrl) return;
  await navigator.clipboard.writeText(studio.shareUrl);
  setDealStudioToast("Link copied");
}

function openShare() {
  if (!studio.shareUrl) return;
  window.open(studio.shareUrl, "_blank", "noopener,noreferrer");
}
</script>

<style scoped>
.deal-studio { display: grid; gap: 14px; padding: 18px; min-height: 100%; }
.deal-studio__header h1 { margin: 6px 0 0; font-size: clamp(28px, 3.2vw, 44px); }
.deal-studio__header p { margin: 8px 0 0; color: rgba(255,255,255,.68); }
.deal-studio__steps { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 8px; }
.step-chip { border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.03); color: rgba(255,255,255,.78); border-radius: 999px; padding: 8px 12px; font-size: 12px; }
.step-chip.is-active { border-color: rgba(240,190,100,.5); background: rgba(240,190,100,.17); color: #f4d8a7; }
.deal-studio__grid { display: grid; grid-template-columns: 1fr 300px; gap: 14px; }
.deal-studio__panel h2 { margin: 0 0 10px; font-size: 22px; }
.muted { color: rgba(255,255,255,.62); margin-top: 0; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.field { display: grid; gap: 6px; margin-bottom: 10px; }
.field label { font-size: 12px; color: rgba(255,255,255,.66); }
.field-select, .field-textarea, .field-readonly { width: 100%; border-radius: 14px; border: 1px solid rgba(255,255,255,.12); background: rgba(12,18,30,.62); color: #dbe5f3; padding: 12px; }
.field-readonly { font-size: 13px; }
.preview-row { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.public-preview, .wallet-preview { border-radius: 18px; border: 1px solid rgba(255,255,255,.09); padding: 12px; background: rgba(255,255,255,.03); }
.public-preview img, .public-preview__img-fallback { width: 100%; height: 180px; border-radius: 12px; object-fit: cover; background: linear-gradient(135deg, rgba(26,42,69,.8), rgba(8,13,24,.95)); }
.public-preview h3 { margin: 10px 0 0; font-size: 20px; }
.public-preview p { margin: 6px 0 0; color: rgba(255,255,255,.7); }
.public-preview .meta { margin-top: 8px; font-size: 13px; color: rgba(255,255,255,.58); }
.public-preview .price { margin-top: 8px; font-size: 24px; font-weight: 700; color: #f4d8a7; }
.wallet-brand { margin: 0; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; color: #f4d8a7; }
.wallet-preview h4 { margin: 8px 0; font-size: 20px; }
.wallet-preview p { margin: 4px 0; color: rgba(255,255,255,.7); }
.wallet-qr { margin-top: 14px; border-radius: 12px; background: rgba(255,255,255,.96); color: #111; display: grid; place-items: center; height: 90px; font-size: 30px; }
.publish-actions { display: flex; gap: 10px; margin: 10px 0; }
.badge { color: #f4d8a7; text-transform: uppercase; letter-spacing: .08em; font-size: 11px; }
.share-grid { display: grid; gap: 10px; }
.share-actions { display: flex; gap: 10px; }
.qr-wrap { border-radius: 14px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.03); min-height: 160px; display: grid; place-items: center; padding: 10px; }
.qr-wrap img { width: 180px; height: 180px; object-fit: contain; }
.qr-wrap--empty { color: rgba(255,255,255,.55); font-size: 13px; }
.nav-actions { margin-top: 16px; display: flex; justify-content: space-between; }
.deal-studio__side h3 { margin-top: 0; }
.deal-studio__side ul { margin: 0 0 14px; padding-left: 16px; color: rgba(255,255,255,.72); }
.toast { position: fixed; right: 20px; bottom: 20px; z-index: 70; border-radius: 12px; border: 1px solid rgba(240,190,100,.3); background: rgba(10,16,28,.92); color: #f4d8a7; padding: 10px 14px; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 180ms ease, transform 180ms ease; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(6px); }
@media (max-width: 1180px) { .deal-studio__grid { grid-template-columns: 1fr; } }
@media (max-width: 767px) {
  .deal-studio { padding: 12px; }
  .field-grid { grid-template-columns: 1fr; }
  .preview-row { grid-template-columns: 1fr; }
  .publish-actions, .share-actions { flex-direction: column; }
}
</style>
