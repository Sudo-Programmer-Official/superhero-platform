<template>
  <section class="flow">
    <article class="card head">
      <p class="eyebrow">Create Offer</p>
      <h1>Publish in 5 steps</h1>
      <p class="sub">Minimal fields first. Advanced setup remains in legacy dashboard.</p>
      <div class="steps">
        <button v-for="n in 5" :key="n" class="step" :class="{ active: step === n, done: n < step }" @click="step = n">{{ n }}</button>
      </div>
    </article>

    <article class="card">
      <template v-if="step === 1">
        <h2>Step 1 · Image</h2>
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
            <p class="tile-title">Cover image</p>
            <p class="hint">{{ uploadingImage ? "Uploading..." : imageUploadState === "uploaded" ? "Uploaded" : "Tap to upload" }}</p>
            <button v-if="localCoverPreviewUrl || form.image" class="btn change-btn" type="button" :disabled="uploadingImage" @click="openCoverPicker">
              Change photo
            </button>
          </div>
        </div>
        <label><span>Or paste image URL (optional)</span><input v-model="form.image" type="url" placeholder="https://..." /></label>
      </template>
      <template v-else-if="step === 2">
        <h2>Step 2 · Title & Description</h2>
        <label><span>Title</span><input v-model="form.title" type="text" placeholder="Offer title" /></label>
        <label><span>Short description</span><textarea v-model="form.description" rows="4" placeholder="A premium wellness experience."></textarea></label>
      </template>
      <template v-else-if="step === 3">
        <h2>Step 3 · Price & Spots</h2>
        <div class="grid">
          <label><span>Price (USD)</span><input v-model="form.price" type="number" min="0" step="0.01" placeholder="45" /></label>
          <label><span>Spots available</span><input v-model="form.capacity" type="number" min="1" step="1" placeholder="20" /></label>
        </div>
      </template>
      <template v-else-if="step === 4">
        <h2>Step 4 · Date & Time</h2>
        <div class="grid">
          <label><span>Start</span><input v-model="form.startsAt" type="datetime-local" /></label>
          <label><span>Duration (minutes)</span><input v-model="form.durationMin" type="number" min="30" step="15" /></label>
          <label><span>Location</span><input v-model="form.location" type="text" placeholder="Los Angeles, CA" /></label>
          <label><span>Timezone</span>
            <select v-model="form.timezone">
              <option v-for="tz in timezoneOptions" :key="tz" :value="tz">{{ tz }}</option>
            </select>
          </label>
        </div>
      </template>
      <template v-else>
        <h2>Step 5 · Publish</h2>
        <p class="sub">Quick publish creates and publishes this offer immediately.</p>
        <button class="btn primary" :disabled="publishing || !canPublish" @click="quickPublish">{{ publishing ? "Publishing..." : "Quick Publish" }}</button>
        <p v-if="shareUrl" class="sub">Published: {{ shareUrl }}</p>
      </template>

      <p v-if="errorText" class="error">{{ errorText }}</p>
      <div class="nav-row">
        <button class="btn" :disabled="step === 1" @click="step -= 1">Back</button>
        <button v-if="step < 5" class="btn primary" @click="goNextStep">Continue</button>
        <button v-else class="btn" type="button" @click="closeAndReturn">Done</button>
      </div>
    </article>

    <article class="card preview">
      <p class="eyebrow">Live Preview</p>
      <img v-if="form.image" :src="form.image" alt="Preview cover" class="cover" />
      <div v-else class="cover fallback"></div>
      <h3>{{ form.title || "Offer title" }}</h3>
      <p class="sub">{{ form.description || "Add a short description for customers." }}</p>
      <p class="meta">{{ priceLabel }} · {{ form.capacity || "0" }} spots</p>
      <p class="meta">{{ scheduleLabel }}</p>
      <p class="meta">{{ form.location || "Add location" }}</p>
    </article>

    <div v-if="successSheetOpen" class="success-overlay" @click.self="successSheetOpen = false">
      <section class="success-sheet" role="dialog" aria-modal="true" aria-label="Offer published">
        <p class="eyebrow">Published</p>
        <h2>Offer is live</h2>
        <p class="sub">Share it now to start bookings.</p>
        <div class="sheet-actions">
          <button class="btn primary" type="button" @click="copyShareLink">Copy Link</button>
          <button class="btn" type="button" @click="sharePublished">Share</button>
          <button class="btn" type="button" @click="previewPublished">Preview</button>
          <button class="btn" type="button" @click="openWalletTab">Open Wallet Tab</button>
        </div>
        <button class="btn" type="button" @click="closeAndReturn">Done</button>
      </section>
    </div>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { formatLocalDateTime, formatTimezone, formatMoney } from "../../domain/deal";
import { createDeal, finalizeAsset, presignUpload, updateDealStatus, uploadFileToPresignedUrl } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

const router = useRouter();
const step = ref(1);
const publishing = ref(false);
const errorText = ref("");
const shareUrl = ref("");
const successSheetOpen = ref(false);
const coverFileInput = ref<HTMLInputElement | null>(null);
const uploadingImage = ref(false);
const imageUploadState = ref<"idle" | "uploaded">("idle");
const localCoverPreviewUrl = ref("");
const pendingImageUpload = ref<{ objectKey: string } | null>(null);

const form = reactive({
  image: "",
  title: "",
  description: "",
  price: "45",
  capacity: "20",
  startsAt: "",
  durationMin: "60",
  location: "",
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC"
});

const timezoneOptions = [
  form.timezone,
  "UTC",
  "America/New_York",
  "America/Chicago",
  "America/Denver",
  "America/Los_Angeles",
  "Europe/London",
  "Asia/Kolkata"
].filter((v, i, arr) => arr.indexOf(v) === i);

const canPublish = computed(() => Boolean(form.title.trim() && form.price && form.capacity && form.startsAt));
const priceLabel = computed(() => formatMoney(form.price || 0, "USD"));
const scheduleLabel = computed(() => {
  if (!form.startsAt) return "Add date and time";
  const startIso = new Date(form.startsAt).toISOString();
  return `${formatLocalDateTime(startIso, form.timezone)} ${formatTimezone(startIso, form.timezone)}`;
});

function endIso(): string {
  const start = form.startsAt ? new Date(form.startsAt).getTime() : Date.now();
  const minutes = Number(form.durationMin || 60);
  return new Date(start + minutes * 60_000).toISOString();
}

function goNextStep() {
  errorText.value = "";
  if (step.value === 1 && !form.image.trim() && !pendingImageUpload.value && !localCoverPreviewUrl.value) {
    errorText.value = "Add a cover image to continue.";
    return;
  }
  if (step.value === 2 && !form.title.trim()) {
    errorText.value = "Add a title to continue.";
    return;
  }
  if (step.value === 3 && (!form.price || !form.capacity)) {
    errorText.value = "Add price and spots to continue.";
    return;
  }
  if (step.value === 4 && !form.startsAt) {
    errorText.value = "Add start date/time to continue.";
    return;
  }
  step.value += 1;
}

function openCoverPicker() {
  coverFileInput.value?.click();
}

async function onCoverFileSelected(event: Event) {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0];
  if (!file) return;
  if (!sessionState.token) {
    showToast("Session expired. Sign in again.", "error");
    return;
  }
  uploadingImage.value = true;
  errorText.value = "";
  try {
    const localPreview = URL.createObjectURL(file);
    localCoverPreviewUrl.value = localPreview;
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
    imageUploadState.value = "idle";
    pendingImageUpload.value = null;
    showToast(`Image upload failed: ${String(err)}`, "error");
  } finally {
    uploadingImage.value = false;
    if (input) input.value = "";
  }
}

async function quickPublish() {
  if (!sessionState.token || !sessionState.me?.practitioner_id) {
    errorText.value = "Session expired. Sign in again.";
    showToast(errorText.value, "error");
    return;
  }
  if (!canPublish.value) {
    errorText.value = "Missing required fields: title, price, spots, and start date/time.";
    showToast(errorText.value, "warning");
    return;
  }
  publishing.value = true;
  errorText.value = "";
  try {
    const draft = await createDeal(sessionState.token, {
      practitioner_id: sessionState.me.practitioner_id,
      title: form.title,
      description: form.description || null,
      image: pendingImageUpload.value ? null : (form.image || null),
      location: form.location || null,
      timezone: form.timezone,
      price: form.price,
      capacity: Number(form.capacity),
      cta_text: "Book now",
      booking_url: null,
      start_time: new Date(form.startsAt).toISOString(),
      end_time: endIso(),
      wallet_enabled: true
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
    shareUrl.value = `${window.location.origin}${published.share_link || `/openmat/${sessionState.me?.practitioner_slug}/${published.slug}`}`;
    showToast("Offer published.", "success");
    successSheetOpen.value = true;
  } catch (err) {
    errorText.value = `Publish failed: ${String(err)}`;
    showToast(errorText.value, "error");
  } finally {
    publishing.value = false;
  }
}

async function copyShareLink() {
  if (!shareUrl.value) return;
  await navigator.clipboard.writeText(shareUrl.value);
  showToast("Offer link copied.", "success");
}

async function sharePublished() {
  if (!shareUrl.value) return;
  if (navigator.share) {
    await navigator.share({ title: form.title || "OpenMat offer", url: shareUrl.value });
    return;
  }
  await copyShareLink();
}

function previewPublished() {
  if (!shareUrl.value) return;
  window.open(shareUrl.value, "_blank", "noopener,noreferrer");
}

function openWalletTab() {
  void router.push({ name: "app-wallet" });
}

function closeAndReturn() {
  successSheetOpen.value = false;
  void router.push({ name: "app-deals" });
}
</script>

<style scoped>
.flow { display: grid; gap: var(--mvp-gap, 14px); padding-bottom: 90px; }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: var(--mvp-radius, 16px); background: rgba(10,20,36,.72); padding: var(--mvp-card-pad, 16px); display: grid; gap: 12px; }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
h1 { margin: 0; font-size: 30px; line-height: 1.03; }
h2 { margin: 0; font-size: 22px; }
.sub { margin: 0; color: rgba(230,238,249,.74); }
.steps { display: flex; gap: 8px; }
.step { width: 34px; height: 34px; border-radius: 999px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.04); color: #dbe5f3; }
.step.active { border-color: rgba(240,190,100,.46); background: rgba(240,190,100,.15); color: #f4d8a7; }
.step.done { border-color: rgba(82,213,139,.42); color: #7ce9af; }
label { display: grid; gap: 6px; }
label span { font-size: 12px; color: rgba(230,238,249,.72); text-transform: uppercase; letter-spacing: .08em; }
input, textarea, select { width: 100%; min-height: var(--mvp-btn-h, 44px); border: 1px solid rgba(255,255,255,.14); border-radius: 12px; background: rgba(7,14,24,.72); color: #e8eef8; padding: 10px 12px; box-sizing: border-box; }
textarea { min-height: 92px; }
.upload-tile {
  border: 1px dashed rgba(255,255,255,.24);
  border-radius: 14px;
  background: rgba(255,255,255,.03);
  padding: 12px;
  display: grid;
  grid-template-columns: auto 1fr;
  gap: 12px;
  align-items: center;
}
.upload-tile.uploading { border-color: rgba(113,182,255,.48); box-shadow: 0 0 0 1px rgba(113,182,255,.22) inset; }
.upload-tile.uploaded { border-color: rgba(82,213,139,.44); box-shadow: 0 0 0 1px rgba(82,213,139,.2) inset; }
.sr-only-file {
  position: absolute;
  width: 1px;
  height: 1px;
  margin: -1px;
  padding: 0;
  border: 0;
  clip: rect(0, 0, 0, 0);
  overflow: hidden;
}
.tile-trigger {
  width: 52px;
  height: 52px;
  border-radius: 14px;
  border: 1px solid rgba(255,255,255,.18);
  background: rgba(255,255,255,.04);
  color: rgba(233,241,252,.86);
  display: grid;
  place-items: center;
}
.camera-icon, .camera-icon svg { width: 22px; height: 22px; display: block; }
.tile-copy { display: grid; gap: 4px; }
.tile-title { margin: 0; font-size: 14px; font-weight: 650; }
.hint { margin: 0; font-size: 12px; color: rgba(230,238,249,.68); }
.change-btn { justify-self: start; min-height: 36px; font-size: 12px; }
.grid { display: grid; gap: 10px; }
.btn { min-height: var(--mvp-btn-h, 44px); border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.btn:disabled { opacity: .52; cursor: not-allowed; }
.nav-row { display: flex; justify-content: space-between; gap: 8px; }
.error { margin: 0; color: #ffb2b2; }
.preview .cover { width: 100%; height: 180px; border-radius: 12px; object-fit: cover; display: block; }
.preview .cover.fallback { background: linear-gradient(135deg, rgba(26,42,69,.8), rgba(8,13,24,.95)); }
.preview h3 { margin: 0; font-size: 22px; }
.meta { margin: 0; font-size: 13px; color: rgba(230,238,249,.74); }
.success-overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(4, 10, 20, 0.64);
  backdrop-filter: blur(6px);
  display: grid;
  align-items: end;
}
.success-sheet {
  border-radius: 20px 20px 0 0;
  border: 1px solid rgba(255,255,255,.14);
  border-bottom: none;
  background: rgba(7,14,24,.98);
  padding: 16px;
  display: grid;
  gap: 12px;
}
.sheet-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
</style>
