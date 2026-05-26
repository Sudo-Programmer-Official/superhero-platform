<template>
  <section class="stack">
    <article class="card hero">
      <p class="eyebrow">Share</p>
      <h1>{{ primaryOffer?.title || "Create your next offer" }}</h1>
      <p class="sub">{{ primaryOffer ? "One clear action: share this live offer." : "Create and publish in under a minute." }}</p>

      <div v-if="primaryOffer" class="offer-hero">
        <img v-if="primaryOffer.image" :src="primaryOffer.image" alt="Offer image" class="cover" />
        <div class="hero-body">
          <p class="meta">{{ formatDate(primaryOffer.start_time) }}<span v-if="primaryOffer.location"> · {{ primaryOffer.location }}</span></p>
          <p class="meta">{{ formatMoney(primaryOffer.base_price, primaryOffer.currency) }} · {{ primaryOffer.remaining_slots }}/{{ primaryOffer.capacity }} left</p>
        </div>
      </div>

      <div class="hero-actions">
        <button class="btn primary" @click="createOffer">Create Offer</button>
        <button class="btn" :disabled="!primaryOffer" @click="copyPrimaryLink">Copy Link</button>
        <button class="btn" :disabled="!primaryOffer" @click="sharePrimary">Share</button>
        <button class="btn" :disabled="!primaryOffer" @click="previewPrimary">Preview</button>
      </div>
    </article>

    <article class="card">
      <div class="head">
        <div>
          <p class="eyebrow">Profile</p>
          <h2>Operator identity</h2>
        </div>
      </div>
      <div class="grid">
        <label>
          <span>Display name</span>
          <input v-model="name" type="text" placeholder="Enter your display name" />
        </label>
        <label>
          <span>Photo</span>
          <div class="upload-tile" :class="{ uploading: uploadingAvatar, uploaded: avatarUploadState === 'uploaded' }">
            <button class="tile-trigger" type="button" @click="openPhotoPicker" :disabled="uploadingAvatar" aria-label="Choose profile photo">
              <img v-if="avatarPreviewUrl" :src="avatarPreviewUrl" alt="Profile photo" class="tile-image" />
              <span v-else class="tile-icon">📷</span>
            </button>
            <div class="tile-meta">
              <p class="hint">{{ uploadingAvatar ? "Uploading..." : avatarUploadState === "uploaded" ? "Uploaded" : "Add photo" }}</p>
              <button v-if="avatarPreviewUrl" class="btn change-btn" type="button" :disabled="uploadingAvatar" @click="openPhotoPicker">
                Change photo
              </button>
            </div>
          </div>
          <input
            ref="photoInput"
            class="hidden-input"
            type="file"
            accept="image/*,.heic,.heif"
            capture="environment"
            @change="onPhotoSelected"
          />
        </label>
      </div>
      <label>
        <span>Short bio</span>
        <textarea v-model="bio" rows="3" placeholder="Add a short bio"></textarea>
      </label>
      <details class="advanced">
        <summary>Advanced settings</summary>
        <p class="hint">Use legacy dashboard for full profile fields and social links.</p>
      </details>
      <div class="row">
        <button class="btn primary" :disabled="saving" @click="saveProfile">{{ saving ? "Saving..." : "Save" }}</button>
        <button class="btn" @click="copyProfileLink">Copy Profile</button>
      </div>
      <p class="hint">{{ saveState }}</p>
    </article>

    <article class="card">
      <div class="head">
        <div>
          <p class="eyebrow">Offers</p>
          <h2>More active offers</h2>
        </div>
      </div>
      <div v-if="loading" class="skeleton-list">
        <div v-for="n in 2" :key="n" class="skeleton shimmer"></div>
      </div>
      <p v-else-if="errorText" class="hint is-error">{{ errorText }}</p>
      <div v-else-if="secondaryOffers.length" class="offers">
        <article v-for="deal in secondaryOffers" :key="deal.id" class="offer-row">
          <p class="title">{{ deal.title }}</p>
          <button class="btn" @click="copyOfferLink(deal.slug)">Copy</button>
        </article>
      </div>
      <p v-else class="hint">No additional active offers.</p>
    </article>

    <button v-if="primaryOffer" class="sticky-share" type="button" @click="sharePrimary">Share Active Offer</button>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, useTemplateRef } from "vue";
import { useRouter } from "vue-router";
import { formatLocalDateTime, formatMoney } from "../../domain/deal";
import {
  fetchPublicPractitioner,
  finalizeAsset,
  listDeals,
  presignUpload,
  updatePractitioner,
  uploadFileToPresignedUrl,
  type DealCardPayload
} from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

const router = useRouter();
const loading = ref(false);
const saving = ref(false);
const errorText = ref("");
const saveState = ref("Saved profile changes keep your page trust-ready.");
const deals = ref<DealCardPayload[]>([]);

const name = ref("");
const avatarUrl = ref("");
const avatarPreviewUrl = ref("");
const bio = ref("");
const photoInput = useTemplateRef<HTMLInputElement>("photoInput");
const uploadingAvatar = ref(false);
const avatarUploadState = ref<"idle" | "uploaded">("idle");

const publishedDeals = computed(() => deals.value.filter((d) => d.status === "published"));
const primaryOffer = computed(() => publishedDeals.value[0] || null);
const secondaryOffers = computed(() => publishedDeals.value.slice(1));

function formatDate(value: string): string {
  return formatLocalDateTime(value, "UTC");
}

function profilePath(): string {
  const slug = sessionState.me?.practitioner_slug || "";
  return `${window.location.origin}/p/${slug}`;
}

function offerPath(slug: string): string {
  const practitionerSlug = sessionState.me?.practitioner_slug || "";
  return `${window.location.origin}/openmat/${practitionerSlug}/${slug}`;
}

async function load() {
  if (!sessionState.token) return;
  loading.value = true;
  errorText.value = "";
  try {
    deals.value = await listDeals(sessionState.token);
    const slug = sessionState.me?.practitioner_slug;
    if (slug) {
      const p = await fetchPublicPractitioner(slug);
      name.value = p.name || "";
      avatarUrl.value = p.avatar_url || p.profile_image || "";
      avatarPreviewUrl.value = avatarUrl.value;
      bio.value = p.bio || "";
    }
  } catch (err) {
    errorText.value = `Failed to load share data: ${String(err)}`;
  } finally {
    loading.value = false;
  }
}

async function saveProfile() {
  if (!sessionState.token || !sessionState.me?.practitioner_id) return;
  saving.value = true;
  try {
    await updatePractitioner(sessionState.token, sessionState.me.practitioner_id, {
      name: name.value || undefined,
      bio: bio.value || null
    });
    saveState.value = "Profile updated.";
    showToast("Profile saved.", "success");
  } catch (err) {
    saveState.value = `Save failed: ${String(err)}`;
    showToast(saveState.value, "error");
  } finally {
    saving.value = false;
  }
}

async function copyProfileLink() {
  await navigator.clipboard.writeText(profilePath());
  showToast("Profile link copied.", "success");
}

async function shareUrl(title: string, url: string) {
  if (navigator.share) {
    await navigator.share({ title, url });
  } else {
    await navigator.clipboard.writeText(url);
    showToast("Link copied.", "success");
  }
}

async function copyOfferLink(slug: string) {
  await navigator.clipboard.writeText(offerPath(slug));
  showToast("Offer link copied.", "success");
}

async function shareOffer(slug: string) {
  await shareUrl("OpenMat offer", offerPath(slug));
}

function previewOffer(slug: string) {
  window.open(offerPath(slug), "_blank", "noopener,noreferrer");
}

async function copyPrimaryLink() {
  if (!primaryOffer.value) return;
  await copyOfferLink(primaryOffer.value.slug);
}

async function sharePrimary() {
  if (!primaryOffer.value) return;
  await shareOffer(primaryOffer.value.slug);
}

function previewPrimary() {
  if (!primaryOffer.value) return;
  previewOffer(primaryOffer.value.slug);
}

function createOffer() {
  void router.push({ name: "operator-offer-create" });
}

function openPhotoPicker() {
  photoInput.value?.click();
}

async function onPhotoSelected(event: Event) {
  const input = event.target as HTMLInputElement | null;
  const file = input?.files?.[0];
  if (!file) return;
  if (!file.type.startsWith("image/")) {
    showToast("Please select an image file.", "warning");
    return;
  }
  if (!sessionState.token || !sessionState.me?.practitioner_id) {
    showToast("Session expired. Sign in again.", "error");
    return;
  }

  const previousPreview = avatarPreviewUrl.value;
  const localPreviewUrl = URL.createObjectURL(file);
  avatarPreviewUrl.value = localPreviewUrl;
  uploadingAvatar.value = true;
  avatarUploadState.value = "idle";

  try {
    const presigned = await presignUpload(sessionState.token, {
      folder: "practitioners",
      filename: file.name || "profile-photo.jpg",
      content_type: file.type || "image/jpeg",
      content_length: file.size
    });

    await uploadFileToPresignedUrl(presigned.upload_url, file, presigned.content_type);
    await finalizeAsset(sessionState.token, {
      target_type: "practitioner",
      target_id: sessionState.me.practitioner_id,
      field_name: "profile_image",
      object_key: presigned.object_key
    });

    avatarUrl.value = presigned.object_key;
    avatarUploadState.value = "uploaded";
    showToast("Profile photo uploaded.", "success");
  } catch (err) {
    avatarPreviewUrl.value = previousPreview;
    URL.revokeObjectURL(localPreviewUrl);
    showToast(`Photo upload failed: ${String(err)}`, "error");
  } finally {
    uploadingAvatar.value = false;
    if (input) input.value = "";
  }
}

onMounted(() => {
  void load();
});
</script>

<style scoped>
.stack { display: grid; gap: var(--mvp-gap, 14px); padding-bottom: 80px; }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: var(--mvp-radius, 16px); background: rgba(10, 20, 36, .72); padding: var(--mvp-card-pad, 16px); display: grid; gap: 12px; }
.hero { background: linear-gradient(170deg, rgba(17, 37, 66, .9), rgba(9, 17, 30, .86)); }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
h1 { margin: 0; font-size: 30px; line-height: 1.03; letter-spacing: -0.02em; }
h2 { margin: 0; font-size: 24px; line-height: 1.05; }
.sub { margin: 0; color: rgba(230,238,249,.78); }
.offer-hero { border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,.14); background: rgba(7,14,24,.72); }
.cover { width: 100%; height: 176px; object-fit: cover; display: block; }
.hero-body { padding: 10px; display: grid; gap: 4px; }
.meta { margin: 0; font-size: 13px; color: rgba(230,238,249,.72); }
.grid { display: grid; gap: 12px; grid-template-columns: 1fr; }
label { display: grid; gap: 6px; }
label span { font-size: 12px; color: rgba(230,238,249,.72); text-transform: uppercase; letter-spacing: .08em; }
input, textarea { width: 100%; min-height: var(--mvp-btn-h, 44px); border: 1px solid rgba(255,255,255,.14); border-radius: 12px; background: rgba(7,14,24,.72); color: #e8eef8; padding: 10px 12px; box-sizing: border-box; }
textarea { min-height: 88px; resize: vertical; }
.photo-picker { display: flex; align-items: center; gap: 10px; }
.upload-tile {
  border: 1px solid rgba(255,255,255,.14);
  border-radius: 14px;
  background: rgba(7,14,24,.72);
  padding: 10px;
  display: flex;
  align-items: center;
  gap: 12px;
  transition: border-color .2s ease, box-shadow .2s ease;
}
.upload-tile.uploading { border-color: rgba(113,182,255,.48); box-shadow: 0 0 0 1px rgba(113,182,255,.22) inset; }
.upload-tile.uploaded { border-color: rgba(82,213,139,.44); box-shadow: 0 0 0 1px rgba(82,213,139,.2) inset; }
.tile-trigger {
  width: 66px;
  height: 66px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,.16);
  background: rgba(255,255,255,.04);
  color: #e8eef8;
  padding: 0;
  display: grid;
  place-items: center;
  overflow: hidden;
}
.tile-image { width: 100%; height: 100%; object-fit: cover; display: block; }
.tile-icon { font-size: 22px; line-height: 1; }
.tile-meta { display: grid; gap: 6px; }
.change-btn { min-height: 36px; padding: 0 10px; font-size: 12px; border-radius: 9px; width: fit-content; }
.hidden-input { display: none; }
.row, .hero-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn { min-height: var(--mvp-btn-h, 44px); border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.btn:disabled { opacity: .5; }
.head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.hint { margin: 0; color: rgba(230,238,249,.72); font-size: 13px; }
.hint.is-error { color: #ffb2b2; }
.offers { display: grid; gap: 8px; }
.offer-row { border: 1px solid rgba(255,255,255,.1); border-radius: 12px; background: rgba(8,14,24,.72); padding: 10px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.title { margin: 0; font-weight: 650; }
.advanced { border: 1px solid rgba(255,255,255,.12); border-radius: 10px; padding: 10px; }
.advanced summary { cursor: pointer; color: rgba(230,238,249,.82); }
.sticky-share {
  position: fixed;
  left: 12px;
  right: 12px;
  bottom: calc(76px + env(safe-area-inset-bottom, 0px));
  z-index: 15;
  min-height: 48px;
  border-radius: 12px;
  border: 1px solid rgba(240,190,100,.46);
  color: #0c1728;
  font-weight: 700;
  background: linear-gradient(145deg, #f3d89f, #e9c57b);
  box-shadow: 0 10px 26px rgba(0,0,0,.25);
}
.skeleton-list { display: grid; gap: 8px; }
.skeleton { height: 80px; border-radius: 12px; border: 1px solid rgba(255,255,255,.08); background: rgba(255,255,255,.04); }
.shimmer { background-image: linear-gradient(100deg, rgba(255,255,255,.03) 20%, rgba(255,255,255,.1) 50%, rgba(255,255,255,.03) 80%); background-size: 200% 100%; animation: shimmer 1.5s linear infinite; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>
