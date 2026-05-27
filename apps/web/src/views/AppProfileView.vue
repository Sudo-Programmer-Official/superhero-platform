<template>
  <section class="stack">
    <article class="card profile-card">
      <div class="avatar-wrap">
        <img v-if="avatarUrl" :src="avatarUrl" alt="Profile photo" class="avatar" />
        <div v-else class="avatar fallback">{{ initials }}</div>
      </div>
      <h1>{{ name || "Your profile" }}</h1>
      <p class="sub">{{ bio || "Add a short bio for your public profile." }}</p>
      <div class="actions">
        <button class="btn" type="button" @click="editing = !editing">{{ editing ? "Done" : "Edit" }}</button>
        <button class="btn" type="button" @click="shareProfile">Share profile</button>
      </div>

      <div v-if="editing" class="edit-grid">
        <input v-model="name" type="text" placeholder="Display name" />
        <div class="upload-tile" :class="{ uploading: uploadingAvatar, uploaded: avatarUploadState === 'uploaded' }">
          <input
            ref="photoInput"
            class="sr-only-file"
            type="file"
            accept="image/*,.heic,.heif"
            capture="environment"
            @change="onPhotoSelected"
          />
          <button class="tile-trigger" type="button" @click="openPhotoPicker" :disabled="uploadingAvatar" aria-label="Choose profile photo">
            <span class="camera-icon" aria-hidden="true">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M4 8h3l1.2-2h7.6L17 8h3a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2v-8a2 2 0 0 1 2-2z" />
                <circle cx="12" cy="14" r="3.5" />
              </svg>
            </span>
          </button>
          <div class="tile-copy">
            <p class="tile-title">Profile photo</p>
            <p class="hint">{{ uploadingAvatar ? "Uploading..." : avatarUploadState === "uploaded" ? "Uploaded" : "Tap to upload" }}</p>
          </div>
        </div>
        <textarea v-model="bio" rows="3" placeholder="Short bio"></textarea>
        <button class="btn primary" :disabled="saving" @click="saveProfile">{{ saving ? "Saving..." : "Save profile" }}</button>
      </div>
    </article>

    <article class="card">
      <div class="head">
        <p class="eyebrow">Active offer</p>
        <button class="btn ghost" type="button" @click="copyDealLink" :disabled="!primaryOffer">Copy link</button>
      </div>
      <div v-if="primaryOffer" class="deal-card">
        <img v-if="primaryOffer.image" :src="primaryOffer.image" alt="Deal image" class="cover" />
        <p class="title">{{ primaryOffer.title }}</p>
        <p class="meta">{{ formatDate(primaryOffer.start_time) }}</p>
        <button class="btn primary" type="button" @click="shareDeal">Share</button>
      </div>
      <p v-else class="sub">No active deal yet. Create one to start sharing.</p>
    </article>

    <article class="card">
      <p class="eyebrow">Advanced</p>
      <button class="btn" type="button" @click="openAdvanced">Open advanced workspace</button>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { formatLocalDateTime } from "../domain/deal";
import { fetchPublicPractitioner, listDeals, updatePractitioner, uploadPractitionerImage, type DealCardPayload } from "../services/api";
import { sessionState } from "../stores/session";
import { showToast } from "../stores/toast";

const router = useRouter();
const saving = ref(false);
const editing = ref(false);
const name = ref("");
const bio = ref("");
const avatarUrl = ref("");
const photoInput = ref<HTMLInputElement | null>(null);
const uploadingAvatar = ref(false);
const avatarUploadState = ref<"idle" | "uploaded">("idle");
const deals = ref<DealCardPayload[]>([]);

const primaryOffer = computed(() => deals.value.find((d) => d.status === "published") || null);
const initials = computed(() => {
  const value = (name.value || "OM").trim();
  return value.split(/\s+/).slice(0, 2).map((part) => part[0]?.toUpperCase() || "").join("") || "OM";
});

function formatDate(value: string): string {
  return formatLocalDateTime(value, "UTC");
}

function dealLink(): string {
  if (!primaryOffer.value) return "";
  const practitionerSlug = sessionState.me?.practitioner_slug || "";
  return `${window.location.origin}/openmat/${practitionerSlug}/${primaryOffer.value.slug}`;
}

async function load() {
  if (!sessionState.token) return;
  deals.value = await listDeals(sessionState.token);
  const slug = sessionState.me?.practitioner_slug;
  if (slug) {
    const p = await fetchPublicPractitioner(slug);
    name.value = p.name || "";
    bio.value = p.bio || "";
    avatarUrl.value = p.avatar_url || p.profile_image || "";
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
    showToast("Profile saved.", "success");
    editing.value = false;
  } catch (err) {
    showToast(`Save failed: ${String(err)}`, "error");
  } finally {
    saving.value = false;
  }
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
  const previous = avatarUrl.value;
  const localPreview = URL.createObjectURL(file);
  avatarUrl.value = localPreview;
  uploadingAvatar.value = true;
  avatarUploadState.value = "idle";
  try {
    const uploaded = await uploadPractitionerImage(sessionState.token, sessionState.me.practitioner_id, file);
    avatarUrl.value = uploaded.avatar_url || uploaded.profile_image || localPreview;
    avatarUploadState.value = "uploaded";
    showToast("Profile photo uploaded.", "success");
  } catch (err) {
    avatarUrl.value = previous;
    showToast(`Photo upload failed: ${String(err)}`, "error");
  } finally {
    uploadingAvatar.value = false;
    if (input) input.value = "";
  }
}

async function shareProfile() {
  const slug = sessionState.me?.practitioner_slug || "";
  const url = `${window.location.origin}/p/${slug}`;
  if (navigator.share) {
    await navigator.share({ title: "OpenMat profile", url });
  } else {
    await navigator.clipboard.writeText(url);
    showToast("Profile link copied.", "success");
  }
}

async function copyDealLink() {
  const url = dealLink();
  if (!url) return;
  await navigator.clipboard.writeText(url);
  showToast("Deal link copied.", "success");
}

async function shareDeal() {
  const url = dealLink();
  if (!url) return;
  if (navigator.share) {
    await navigator.share({ title: primaryOffer.value?.title || "OpenMat offer", url });
  } else {
    await navigator.clipboard.writeText(url);
    showToast("Deal link copied.", "success");
  }
}

function openAdvanced() {
  void router.push({ name: "dashboard" });
}

onMounted(() => {
  void load();
});
</script>

<style scoped>
.stack { display: grid; gap: 14px; }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: 16px; background: rgba(10,20,36,.72); padding: 16px; display: grid; gap: 12px; }
.profile-card { justify-items: center; text-align: center; }
.avatar-wrap { width: 92px; height: 92px; border-radius: 999px; border: 1px solid rgba(255,255,255,.2); overflow: hidden; background: rgba(255,255,255,.06); }
.avatar { width: 100%; height: 100%; object-fit: cover; }
.avatar.fallback { display: grid; place-items: center; font-weight: 700; color: #f4d8a7; height: 100%; }
h1 { margin: 0; font-size: 28px; line-height: 1.05; }
.sub { margin: 0; color: rgba(230,238,249,.75); }
.actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
.edit-grid { width: 100%; display: grid; gap: 10px; }
input, textarea { width: 100%; min-height: 44px; border: 1px solid rgba(255,255,255,.14); border-radius: 12px; background: rgba(7,14,24,.72); color: #e8eef8; padding: 10px 12px; box-sizing: border-box; }
textarea { min-height: 88px; resize: vertical; }
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
.tile-copy { display: grid; gap: 4px; text-align: left; }
.tile-title { margin: 0; font-size: 14px; font-weight: 650; }
.hint { margin: 0; font-size: 12px; color: rgba(230,238,249,.68); }
.head { display: flex; align-items: center; justify-content: space-between; gap: 8px; }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
.deal-card { display: grid; gap: 8px; }
.cover { width: 100%; height: 180px; object-fit: cover; border-radius: 12px; }
.title { margin: 0; font-size: 20px; font-weight: 700; }
.meta { margin: 0; color: rgba(230,238,249,.72); font-size: 13px; }
.btn { min-height: 44px; border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.btn.ghost { min-height: 36px; font-size: 12px; }
</style>
