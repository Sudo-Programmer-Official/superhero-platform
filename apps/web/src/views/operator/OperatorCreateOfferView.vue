<template>
  <section class="composer-shell">
    <article class="preview-card">
      <p class="eyebrow">Live preview</p>
      <div class="preview-frame">
        <img v-if="form.image" :src="form.image" alt="Deal preview cover" class="cover" />
        <div v-else class="cover cover--fallback"></div>
      </div>
      <div class="preview-copy">
        <p class="preview-title">{{ previewTitle }}</p>
        <p class="preview-offer">{{ previewOffer }}</p>
        <div class="preview-meta">
          <span>{{ previewExpiry }}</span>
          <span>{{ previewLocation }}</span>
        </div>
      </div>
    </article>

    <article class="composer-card">
      <p class="eyebrow">Create deal</p>
      <h1>Post a promotion</h1>
      <p class="sub">Upload a cover, add a title, and publish like you are posting content.</p>

      <div class="upload-tile" :class="{ uploading: uploadingImage, uploaded: imageUploadState === 'uploaded' }">
        <input
          ref="coverFileInput"
          class="sr-only-file"
          type="file"
          accept="image/*"
          capture="environment"
          @change="onCoverFileSelected"
        />
        <button class="tile-trigger" type="button" @click="openCoverPicker" :disabled="uploadingImage" aria-label="Choose cover image">
          <span class="camera-icon" aria-hidden="true">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M4 8h3l1.2-2h7.6L17 8h3a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2z" />
              <circle cx="12" cy="14" r="3.5" />
            </svg>
          </span>
        </button>
        <div class="tile-copy">
          <p class="tile-title">Upload photo</p>
          <p class="hint">{{ uploadingImage ? "Uploading..." : imageUploadState === "uploaded" ? "Uploaded" : "Tap to upload" }}</p>
        </div>
      </div>

      <div class="field-grid">
        <label class="field">
          <span>Deal title</span>
          <input v-model="form.title" type="text" placeholder="Summer of 26 Promotion" />
        </label>
        <label class="field">
          <span>Offer / price</span>
          <input v-model="form.price" type="number" min="0" step="0.01" placeholder="45" />
        </label>
        <label class="field">
          <span>Date</span>
          <input v-model="form.expiresOn" type="date" />
        </label>
        <label class="field">
          <span>Location</span>
          <input v-model="form.location" type="text" placeholder="Delray Beach, FL" />
        </label>
      </div>

      <label class="field">
        <span>Description</span>
        <textarea v-model="form.description" rows="3" placeholder="10% Off Popular Services"></textarea>
      </label>

      <details class="more-options">
        <summary>More options</summary>
        <div class="more-grid">
          <label class="field">
            <span>Capacity</span>
            <input v-model="form.capacity" type="number" min="1" step="1" placeholder="20" />
          </label>
          <label class="field">
            <span>Timezone</span>
            <select v-model="form.timezone" class="select">
              <option v-for="tz in timezoneOptions" :key="tz" :value="tz">{{ tz }}</option>
            </select>
          </label>
          <label class="field">
            <span>Wallet pass</span>
            <select v-model="form.walletEnabled" class="select">
              <option :value="true">Enabled</option>
              <option :value="false">Disabled</option>
            </select>
          </label>
          <label class="field">
            <span>Visibility</span>
            <select v-model="form.visibility" class="select">
              <option value="public">Public</option>
              <option value="private">Private</option>
            </select>
          </label>
          <label class="field more-details">
            <span>Additional details</span>
            <textarea v-model="form.additionalDetails" rows="3" placeholder="Service list, exclusions, or anything else."></textarea>
          </label>
        </div>
      </details>

      <p v-if="errorText" class="error">{{ errorText }}</p>

      <div class="actions">
        <button class="btn ghost" type="button" @click="closeAndReturn">Back</button>
        <button class="btn primary" :disabled="publishing || !canPublish" @click="publishDeal">
          {{ publishing ? "Publishing..." : "Publish deal" }}
        </button>
      </div>

      <div v-if="studio.shareUrl" class="share-row">
        <div class="share-field">
          <span>Public URL</span>
          <input class="share-input" :value="studio.shareUrl" readonly />
        </div>
        <div class="share-actions">
          <button class="btn ghost" type="button" :disabled="!studio.shareUrl" @click="copyShare">Copy link</button>
          <button class="btn ghost" type="button" :disabled="!studio.shareUrl" @click="openShare">Open page</button>
        </div>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { createDeal, finalizeAsset, presignUpload, updateDealStatus, uploadFileToPresignedUrl } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";
import { dealStudioState as studio, resetDealStudio } from "../../stores/dealStudio";

const router = useRouter();
const publishing = ref(false);
const errorText = ref("");
const coverFileInput = ref<HTMLInputElement | null>(null);
const uploadingImage = ref(false);
const imageUploadState = ref<"idle" | "uploaded">("idle");
const pendingImageUpload = ref<{ objectKey: string } | null>(null);

const form = reactive({
  image: "",
  title: "",
  description: "",
  price: "45",
  capacity: "20",
  expiresOn: "",
  location: "",
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
  walletEnabled: true,
  visibility: "public",
  additionalDetails: ""
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

const previewTitle = computed(() => form.title.trim() || "Summer of 26 Promotion");
const previewOffer = computed(() => form.description.trim() || "10% Off Popular Services");
const previewExpiry = computed(() => {
  if (!form.expiresOn) return "Expires July 7";
  return `Expires ${new Date(`${form.expiresOn}T12:00:00`).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric"
  })}`;
});
const previewLocation = computed(() => form.location.trim() || "Delray Beach, FL");

const canPublish = computed(() => Boolean(form.title.trim() && form.price && form.expiresOn && form.location.trim()));

function openCoverPicker() {
  coverFileInput.value?.click();
}

function endIso(): string {
  const end = form.expiresOn ? new Date(`${form.expiresOn}T23:59:59`) : new Date();
  return end.toISOString();
}

function startIso(): string {
  return new Date().toISOString();
}

async function onCoverFileSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file || !sessionState.token) return;
  uploadingImage.value = true;
  errorText.value = "";
  try {
    const localPreview = URL.createObjectURL(file);
    form.image = localPreview;
    imageUploadState.value = "idle";
    const presign = await presignUpload(sessionState.token, {
      folder: "deals",
      filename: file.name,
      content_type: file.type || "image/jpeg",
      content_length: file.size
    });
    await uploadFileToPresignedUrl(presign.upload_url, file, presign.content_type || file.type || "image/jpeg");
    pendingImageUpload.value = { objectKey: presign.object_key };
    imageUploadState.value = "uploaded";
    showToast("Cover image uploaded.", "success");
  } catch (err) {
    pendingImageUpload.value = null;
    imageUploadState.value = "idle";
    showToast(`Image upload failed: ${String(err)}`, "error");
  } finally {
    uploadingImage.value = false;
    if (input) input.value = "";
  }
}

async function publishDeal() {
  if (!sessionState.token || !sessionState.me?.practitioner_id) {
    errorText.value = "Session expired. Sign in again.";
    return;
  }
  if (!canPublish.value) {
    errorText.value = "Add title, offer, date, and location.";
    return;
  }
  publishing.value = true;
  errorText.value = "";
  try {
    const draft = await createDeal(sessionState.token, {
      practitioner_id: sessionState.me.practitioner_id,
      title: form.title.trim(),
      description: [form.description.trim(), form.additionalDetails.trim()].filter(Boolean).join("\n\n") || null,
      image: pendingImageUpload.value ? null : (form.image || null),
      location: form.location.trim() || null,
      timezone: form.timezone,
      price: form.price,
      capacity: Number(form.capacity || 0),
      cta_text: "Save Pass",
      booking_url: null,
      start_time: startIso(),
      end_time: endIso(),
      wallet_enabled: form.walletEnabled
    });
    if (pendingImageUpload.value) {
      await finalizeAsset(sessionState.token, {
        target_type: "deal_card",
        target_id: draft.id,
        field_name: "image",
        object_key: pendingImageUpload.value.objectKey
      });
    }
    const published = await updateDealStatus(sessionState.token, draft.id, "published");
    studio.lastDraftId = published.id;
    studio.shareUrl = published.share_link || published.public_url || `${window.location.origin}/openmat/${sessionState.me.practitioner_slug || ""}/${published.slug}`;
    studio.status = "done";
    showToast("Deal published.", "success");
    void router.push({ name: "app-deals" });
  } catch (err) {
    errorText.value = `Publish failed: ${String(err)}`;
    showToast(errorText.value, "error");
    studio.status = "idle";
  } finally {
    publishing.value = false;
  }
}

async function copyShare() {
  if (!studio.shareUrl) return;
  try {
    await navigator.clipboard.writeText(studio.shareUrl);
    showToast("Link copied.", "success");
  } catch {
    showToast("Could not copy link.", "error");
  }
}

function openShare() {
  if (!studio.shareUrl) return;
  window.open(studio.shareUrl, "_blank", "noopener,noreferrer");
}

function closeAndReturn() {
  resetDealStudio();
  void router.push({ name: "app-deals" });
}
</script>

<style scoped>
.composer-shell { display: grid; gap: 14px; padding-bottom: calc(108px + env(safe-area-inset-bottom, 0px)); }
.preview-card, .composer-card {
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 18px;
  background: rgba(10,20,36,.72);
  padding: 16px;
  display: grid;
  gap: 12px;
}
.preview-card { padding: 0; overflow: hidden; }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; padding: 16px 16px 0; }
.preview-frame { aspect-ratio: 1 / 1; background: linear-gradient(135deg, rgba(26,42,69,.8), rgba(8,13,24,.95)); overflow: hidden; }
.cover { width: 100%; height: 100%; object-fit: cover; display: block; }
.cover--fallback { background: radial-gradient(circle at 30% 20%, rgba(240,190,100,.16), transparent 36%), linear-gradient(135deg, rgba(26,42,69,.8), rgba(8,13,24,.95)); }
.preview-copy { padding: 14px 16px 16px; display: grid; gap: 6px; }
.preview-title { margin: 0; font-size: 24px; font-weight: 700; line-height: 1.05; letter-spacing: -0.02em; }
.preview-offer { margin: 0; font-size: 15px; color: rgba(230,238,249,.82); }
.preview-meta { display: flex; flex-wrap: wrap; gap: 8px; color: rgba(230,238,249,.64); font-size: 13px; }
.preview-meta span { padding: 6px 10px; border-radius: 999px; background: rgba(255,255,255,.05); border: 1px solid rgba(255,255,255,.08); }
h1 { margin: 0; font-size: 28px; line-height: 1.05; letter-spacing: -0.02em; }
.sub { margin: 0; color: rgba(230,238,249,.74); }
.upload-tile {
  border: 1px dashed rgba(255,255,255,.24);
  border-radius: 16px;
  background: rgba(255,255,255,.03);
  padding: 12px;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  align-items: center;
}
.upload-tile.uploading { border-color: rgba(113,182,255,.48); box-shadow: 0 0 0 1px rgba(113,182,255,.22) inset; }
.upload-tile.uploaded { border-color: rgba(82,213,139,.44); box-shadow: 0 0 0 1px rgba(82,213,139,.2) inset; }
.sr-only-file { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; border: 0; clip: rect(0, 0, 0, 0); overflow: hidden; }
.tile-trigger { width: 52px; height: 52px; border-radius: 14px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.04); color: rgba(233,241,252,.86); display: grid; place-items: center; }
.camera-icon, .camera-icon svg { width: 22px; height: 22px; display: block; }
.tile-copy { display: grid; gap: 4px; }
.tile-title { margin: 0; font-size: 14px; font-weight: 650; }
.hint { margin: 0; font-size: 12px; color: rgba(230,238,249,.68); }
.field-grid, .more-grid { display: grid; gap: 10px; }
.field { display: grid; gap: 6px; }
.field span { font-size: 12px; color: rgba(230,238,249,.72); text-transform: uppercase; letter-spacing: .08em; }
input, textarea, select, .share-input {
  width: 100%;
  min-height: 44px;
  border: 1px solid rgba(255,255,255,.14);
  border-radius: 12px;
  background: rgba(7,14,24,.72);
  color: #e8eef8;
  padding: 10px 12px;
  box-sizing: border-box;
}
textarea { min-height: 92px; resize: vertical; }
.select { appearance: none; }
.more-options {
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 16px;
  background: rgba(255,255,255,.03);
  padding: 12px;
}
.more-options summary {
  cursor: pointer;
  list-style: none;
  color: #f4d8a7;
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: .1em;
}
.more-options summary::-webkit-details-marker { display: none; }
.more-grid { margin-top: 12px; }
.more-details { grid-column: 1 / -1; }
.actions { display: flex; gap: 8px; justify-content: space-between; flex-wrap: wrap; }
.btn {
  min-height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.05);
  color: #e8eef8;
  padding: 0 12px;
}
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.btn.ghost { width: fit-content; }
.btn:disabled { opacity: .52; cursor: not-allowed; }
.error { margin: 0; color: #ffb2b2; }
.share-row {
  border-top: 1px solid rgba(255,255,255,.1);
  padding-top: 12px;
  display: grid;
  gap: 10px;
}
.share-field { display: grid; gap: 6px; }
.share-field span { font-size: 12px; color: rgba(230,238,249,.72); text-transform: uppercase; letter-spacing: .08em; }
.share-actions { display: flex; gap: 8px; flex-wrap: wrap; }
@media (min-width: 720px) {
  .field-grid, .more-grid { grid-template-columns: 1fr 1fr; }
}
</style>
