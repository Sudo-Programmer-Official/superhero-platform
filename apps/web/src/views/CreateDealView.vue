<template>
  <DashboardPageShell
    eyebrow="Deal Studio"
    title="Create Deal"
    subtitle="Build, validate, and publish high-conversion campaigns from one production-ready workflow."
  >
    <div class="studio-layout">
      <section class="studio-main">
        <AppCard class="studio-card">
          <div class="section-head">
            <h2>Basic Info</h2>
            <p>Define the core identity and messaging for this deal.</p>
          </div>
          <div class="field-grid">
            <div class="field"><label>Title</label><AppInput v-model="studio.form.title" placeholder="Breathwork Journey" /></div>
            <div class="field"><label>Category</label><AppInput v-model="studio.form.category" placeholder="Breathwork" /></div>
            <div class="field"><label>Location</label><AppInput v-model="studio.form.location" placeholder="Los Angeles, CA" /></div>
            <div class="field"><label>Cover image URL</label><AppInput v-model="studio.form.coverImage" placeholder="https://..." /></div>
          </div>
          <div class="field"><label>Description</label><textarea v-model="studio.form.description" rows="4" class="field-textarea" placeholder="Describe the experience"></textarea></div>
        </AppCard>

        <AppCard class="studio-card">
          <div class="section-head">
            <h2>Schedule</h2>
            <p>Set timing details with clear timezone context.</p>
          </div>
          <div class="field-grid">
            <div class="field"><label>Start</label><AppInput v-model="studio.form.startsAt" type="datetime-local" /></div>
            <div class="field"><label>End</label><AppInput v-model="studio.form.endsAt" type="datetime-local" /></div>
            <div class="field">
              <label>Timezone</label>
              <select v-model="studio.form.timezone" class="field-select">
                <option v-for="tz in timezoneOptions" :key="tz" :value="tz">{{ tz }}</option>
              </select>
            </div>
          </div>
        </AppCard>

        <AppCard class="studio-card">
          <div class="section-head">
            <h2>Capacity & Pricing</h2>
            <p>Balance inventory and pricing to optimize conversion.</p>
          </div>
          <div class="field-grid">
            <div class="field"><label>Seats</label><AppInput v-model="studio.form.seats" type="number" placeholder="20" /></div>
            <div class="field"><label>Pricing (USD)</label><AppInput v-model="studio.form.price" type="number" placeholder="45.00" /></div>
          </div>
        </AppCard>

        <AppCard class="studio-card">
          <div class="section-head">
            <h2>Redemption</h2>
            <p>Choose your on-site validation flow.</p>
          </div>
          <div class="field-grid">
            <div class="field">
              <label>Redemption type</label>
              <select v-model="studio.form.redemptionType" class="field-select"><option value="qr">QR</option><option value="nfc">NFC</option></select>
            </div>
          </div>
        </AppCard>

        <AppCard class="studio-card">
          <div class="section-head">
            <h2>Visibility</h2>
            <p>Control how and when this campaign appears publicly.</p>
          </div>
          <div class="field-grid">
            <div class="field">
              <label>Visibility</label>
              <select v-model="studio.form.visibility" class="field-select"><option value="public">Public</option><option value="private">Private</option></select>
            </div>
          </div>
        </AppCard>

        <AppCard class="studio-card">
          <div class="section-head">
            <h2>Preview</h2>
            <p>Live preview of the public card and wallet pass output.</p>
          </div>
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
        </AppCard>
      </section>

      <aside class="studio-side">
        <AppCard class="workflow-card" muted>
          <h3>Workflow State</h3>
          <p class="workflow-sub">Operational readiness</p>
          <div class="progress-wrap">
            <div class="progress-track"><div class="progress-fill" :style="{ width: `${completion}%` }"></div></div>
            <p>{{ completion }}% complete</p>
          </div>
          <ul>
            <li><span>Status</span><strong>{{ studio.status }}</strong></li>
            <li><span>Draft</span><strong>{{ studio.lastDraftId ? 'created' : 'missing' }}</strong></li>
            <li><span>Share</span><strong>{{ studio.shareUrl ? 'ready' : 'pending' }}</strong></li>
            <li><span>Visibility</span><strong>{{ studio.form.visibility }}</strong></li>
          </ul>
          <div class="publish-actions">
            <AppButton variant="secondary" :disabled="studio.status === 'saving' || studio.status === 'publishing'" @click="onCreateDraft">
              {{ studio.status === 'saving' ? 'Creating draft...' : 'Create draft' }}
            </AppButton>
            <AppButton variant="primary" :disabled="!studio.lastDraftId || studio.status === 'publishing'" @click="onPublish">
              {{ studio.status === 'publishing' ? 'Publishing...' : 'Publish deal' }}
            </AppButton>
          </div>
          <div class="share-grid">
            <div class="field"><label>Public URL</label><input class="field-readonly" :value="studio.shareUrl" readonly /></div>
            <div class="share-actions">
              <AppButton variant="ghost" :disabled="!studio.shareUrl" @click="copyShare">Copy link</AppButton>
              <AppButton variant="ghost" :disabled="!studio.shareUrl" @click="openShare">Open page</AppButton>
            </div>
          </div>
          <AppButton variant="ghost" @click="resetDealStudio">Reset flow</AppButton>
        </AppCard>
      </aside>
    </div>

    <transition name="toast-fade">
      <div v-if="studio.toast" class="toast">{{ studio.toast }}</div>
    </transition>
  </DashboardPageShell>
</template>

<script setup lang="ts">
import { computed } from "vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import AppInput from "../design-system/primitives/AppInput.vue";
import DashboardPageShell from "../design-system/patterns/DashboardPageShell.vue";
import { formatLocalDateTime, formatTimezone } from "../domain/deal";
import { createDeal, updateDealStatus } from "../services/api";
import { dealStudioState as studio, resetDealStudio, setDealStudioToast } from "../stores/dealStudio";
import { sessionState } from "../stores/session";

const formattedStart = computed(() => {
  if (!studio.form.startsAt) return "Date pending";
  const iso = new Date(studio.form.startsAt).toISOString();
  return `${formatLocalDateTime(iso, studio.form.timezone)} ${formatTimezone(iso, studio.form.timezone)}`;
});

const completion = computed(() => {
  let points = 0;
  if (studio.form.title.trim()) points += 16;
  if (studio.form.description.trim()) points += 16;
  if (studio.form.startsAt && studio.form.endsAt) points += 16;
  if (studio.form.price && studio.form.seats) points += 16;
  if (studio.lastDraftId) points += 18;
  if (studio.shareUrl) points += 18;
  return points;
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
.studio-layout { display: grid; grid-template-columns: minmax(0, 1fr) 340px; gap: 24px; }
.studio-main { display: grid; gap: 24px; }
.studio-card { display: grid; gap: 20px; }
.section-head { display: grid; gap: 12px; }
.section-head h2 { margin: 0; font-size: 24px; letter-spacing: -0.01em; }
.section-head p { margin: 0; color: rgba(255,255,255,.66); font-size: 14px; }
.field-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.field { display: grid; gap: 8px; }
.field label { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: rgba(255,255,255,.62); }
.field-select, .field-textarea, .field-readonly { width: 100%; min-height: 48px; border-radius: 14px; border: 1px solid rgba(255,255,255,.12); background: rgba(12,18,30,.62); color: #dbe5f3; padding: 12px; }
.field-readonly { font-size: 13px; }
.preview-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.public-preview, .wallet-preview { border-radius: 18px; border: 1px solid rgba(255,255,255,.09); padding: 16px; background: rgba(255,255,255,.03); transition: transform 180ms ease, box-shadow 180ms ease, opacity 180ms ease; }
.public-preview:hover, .wallet-preview:hover { transform: translateY(-2px); box-shadow: 0 16px 36px rgba(0,0,0,.28); }
.public-preview img, .public-preview__img-fallback { width: 100%; height: 180px; border-radius: 12px; object-fit: cover; background: linear-gradient(135deg, rgba(26,42,69,.8), rgba(8,13,24,.95)); }
.public-preview h3 { margin: 12px 0 0; font-size: 20px; }
.public-preview p { margin: 8px 0 0; color: rgba(255,255,255,.7); }
.public-preview .meta { margin-top: 12px; font-size: 13px; color: rgba(255,255,255,.58); }
.public-preview .price { margin-top: 12px; font-size: 24px; font-weight: 700; color: #f4d8a7; }
.wallet-brand { margin: 0; font-size: 12px; letter-spacing: .1em; text-transform: uppercase; color: #f4d8a7; }
.wallet-preview h4 { margin: 8px 0 12px; font-size: 20px; }
.wallet-preview p { margin: 4px 0; color: rgba(255,255,255,.7); }
.wallet-qr { margin-top: 16px; border-radius: 12px; background: rgba(255,255,255,.96); color: #111; display: grid; place-items: center; height: 96px; font-size: 30px; }
.studio-side { position: relative; }
.workflow-card { position: sticky; top: 24px; display: grid; gap: 16px; }
.workflow-card h3 { margin: 0; font-size: 20px; }
.workflow-sub { margin: 0; color: rgba(255,255,255,.62); font-size: 13px; }
.progress-wrap { display: grid; gap: 8px; }
.progress-wrap p { margin: 0; font-size: 12px; color: rgba(255,255,255,.66); }
.progress-track { height: 8px; border-radius: 999px; background: rgba(255,255,255,.08); overflow: hidden; }
.progress-fill { height: 100%; border-radius: inherit; background: linear-gradient(90deg, rgba(240,190,100,.86), rgba(112,214,153,.9)); transition: width 220ms ease; }
.workflow-card ul { margin: 0; padding: 0; list-style: none; display: grid; gap: 12px; }
.workflow-card li { display: flex; justify-content: space-between; gap: 12px; font-size: 13px; color: rgba(255,255,255,.75); }
.workflow-card li strong { text-transform: capitalize; color: #f4d8a7; font-weight: 600; }
.publish-actions { display: grid; gap: 12px; }
.share-grid { display: grid; gap: 12px; }
.share-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.toast { position: fixed; right: 20px; bottom: 20px; z-index: 70; border-radius: 12px; border: 1px solid rgba(240,190,100,.3); background: rgba(10,16,28,.92); color: #f4d8a7; padding: 10px 14px; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 180ms ease, transform 180ms ease; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(6px); }
@media (max-width: 1279px) {
  .studio-layout { grid-template-columns: 1fr; }
  .workflow-card { position: static; }
}
@media (max-width: 1023px) {
  .field-grid, .preview-row, .share-actions { grid-template-columns: 1fr; }
}
</style>
