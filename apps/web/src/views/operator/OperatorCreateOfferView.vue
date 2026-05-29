<template>
  <section class="flow">
    <article class="card preview">
      <p class="eyebrow">App Preview</p>
      <img v-if="form.image" :src="form.image" alt="Preview cover" class="cover" />
      <div v-else class="cover fallback"></div>
      <div class="preview-body">
        <p class="title">{{ form.title || "Deal title" }}</p>
        <p class="meta">{{ priceLabel }} · {{ form.capacity || "0" }} spots</p>
        <p class="meta">{{ scheduleLabel }}</p>
        <p class="meta">{{ form.location || "Add location" }}</p>
      </div>
    </article>

    <article class="card">
      <p class="eyebrow">Create Offer</p>
      <h1>Publish in 5 steps</h1>
      <div class="steps">
        <span class="step done">1</span>
        <span class="step done">2</span>
        <span class="step done">3</span>
        <span class="step done">4</span>
        <span class="step active">5</span>
      </div>

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
          <p class="tile-title">Add photo</p>
          <p class="hint">{{ uploadingImage ? "Uploading..." : imageUploadState === "uploaded" ? "Uploaded" : "Tap to upload" }}</p>
        </div>
      </div>

      <div class="grid">
        <label><span>Title</span><input v-model="form.title" type="text" placeholder="Deal title" /></label>
        <label><span>Price</span><input v-model="form.price" type="number" min="0" step="0.01" placeholder="45" /></label>
        <label><span>Quantity</span><input v-model="form.capacity" type="number" min="1" step="1" placeholder="20" /></label>
        <label><span>Date & time</span><input v-model="form.startsAt" type="datetime-local" /></label>
        <label><span>Location</span><input v-model="form.location" type="text" placeholder="Austin, TX" /></label>
        <label><span>Description</span><textarea v-model="form.description" rows="3" placeholder="Short description"></textarea></label>
      </div>

      <p v-if="errorText" class="error">{{ errorText }}</p>
      <div class="row">
        <button class="btn" type="button" @click="closeAndReturn">Back</button>
        <button class="btn primary" :disabled="publishing || !canPublish" @click="quickPublish">{{ publishing ? "Publishing..." : "Update Offer" }}</button>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useRouter } from "vue-router";
import { formatLocalDateTime, formatMoney, formatTimezone } from "../../domain/deal";
import { createDeal, finalizeAsset, presignUpload, updateDealStatus, uploadFileToPresignedUrl } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

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
  startsAt: "",
  durationMin: "60",
  location: "",
  timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC"
});

const canPublish = computed(() => Boolean(form.title.trim() && form.price && form.capacity && form.startsAt));
const priceLabel = computed(() => formatMoney(form.price || 0, "USD"));
const scheduleLabel = computed(() => {
  if (!form.startsAt) return "Add date and time";
  const startIso = new Date(form.startsAt).toISOString();
  return `${formatLocalDateTime(startIso, form.timezone)} ${formatTimezone(startIso, form.timezone)}`;
});

function openCoverPicker() {
  coverFileInput.value?.click();
}

function endIso(): string {
  const start = form.startsAt ? new Date(form.startsAt).getTime() : Date.now();
  const minutes = Number(form.durationMin || 60);
  return new Date(start + minutes * 60_000).toISOString();
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

async function quickPublish() {
  if (!sessionState.token || !sessionState.me?.practitioner_id) {
    errorText.value = "Session expired. Sign in again.";
    return;
  }
  if (!canPublish.value) {
    errorText.value = "Add title, price, spots, and date/time.";
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
    await updateDealStatus(sessionState.token, draft.id, "published");
    showToast("Offer published.", "success");
    void router.push({ name: "app-deals" });
  } catch (err) {
    errorText.value = `Publish failed: ${String(err)}`;
    showToast(errorText.value, "error");
  } finally {
    publishing.value = false;
  }
}

function closeAndReturn() {
  void router.push({ name: "app-deals" });
}
</script>

<style scoped>
.flow { display: grid; gap: var(--mvp-gap, 14px); padding-bottom: 90px; }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: var(--mvp-radius, 16px); background: rgba(10,20,36,.72); padding: var(--mvp-card-pad, 16px); display: grid; gap: 12px; }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
h1 { margin: 0; font-size: 28px; line-height: 1.06; }
.preview { padding: 0; overflow: hidden; }
.cover { width: 100%; height: 190px; object-fit: cover; display: block; }
.cover.fallback { background: linear-gradient(135deg, rgba(26,42,69,.8), rgba(8,13,24,.95)); }
.preview-body { padding: 12px 14px 14px; display: grid; gap: 4px; }
.title { margin: 0; font-size: 22px; font-weight: 700; }
.meta { margin: 0; color: rgba(230,238,249,.72); font-size: 13px; }
.steps { display: flex; gap: 8px; }
.step { width: 30px; height: 30px; border-radius: 999px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.04); color: #dbe5f3; display: grid; place-items: center; font-size: 12px; }
.step.active { border-color: rgba(240,190,100,.46); background: rgba(240,190,100,.15); color: #f4d8a7; }
.step.done { border-color: rgba(82,213,139,.42); color: #7ce9af; }
.upload-tile { border: 1px dashed rgba(255,255,255,.24); border-radius: 14px; background: rgba(255,255,255,.03); padding: 12px; display: grid; grid-template-columns: auto 1fr; gap: 12px; align-items: center; }
.upload-tile.uploading { border-color: rgba(113,182,255,.48); box-shadow: 0 0 0 1px rgba(113,182,255,.22) inset; }
.upload-tile.uploaded { border-color: rgba(82,213,139,.44); box-shadow: 0 0 0 1px rgba(82,213,139,.2) inset; }
.sr-only-file { position: absolute; width: 1px; height: 1px; margin: -1px; padding: 0; border: 0; clip: rect(0, 0, 0, 0); overflow: hidden; }
.tile-trigger { width: 52px; height: 52px; border-radius: 14px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.04); color: rgba(233,241,252,.86); display: grid; place-items: center; }
.camera-icon, .camera-icon svg { width: 22px; height: 22px; display: block; }
.tile-copy { display: grid; gap: 4px; }
.tile-title { margin: 0; font-size: 14px; font-weight: 650; }
.hint { margin: 0; font-size: 12px; color: rgba(230,238,249,.68); }
.grid { display: grid; gap: 10px; }
label { display: grid; gap: 6px; }
label span { font-size: 12px; color: rgba(230,238,249,.72); text-transform: uppercase; letter-spacing: .08em; }
input, textarea { width: 100%; min-height: var(--mvp-btn-h, 44px); border: 1px solid rgba(255,255,255,.14); border-radius: 12px; background: rgba(7,14,24,.72); color: #e8eef8; padding: 10px 12px; box-sizing: border-box; }
textarea { min-height: 88px; resize: vertical; }
.row { display: flex; gap: 8px; justify-content: space-between; }
.btn { min-height: var(--mvp-btn-h, 44px); border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.btn:disabled { opacity: .52; cursor: not-allowed; }
.error { margin: 0; color: #ffb2b2; }
</style>
