<template>
  <section class="stack">
    <article class="card profile-card">
      <div class="avatar-wrap">
        <img v-if="avatarUrl" :src="avatarUrl" alt="Profile photo" class="avatar" />
        <div v-else class="avatar fallback">{{ initials }}</div>
      </div>
      <h1>{{ name || "Your business" }}</h1>
      <p class="sub">{{ bio || "Add a short description for your public profile." }}</p>
      <div class="actions">
        <button class="btn" type="button" @click="editProfile">Edit Profile</button>
        <button class="btn primary" type="button" @click="shareProfile">Share Profile</button>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { fetchPublicPractitioner } from "../services/api";
import { sessionState } from "../stores/session";
import { showToast } from "../stores/toast";

const router = useRouter();
const name = ref("");
const bio = ref("");
const avatarUrl = ref("");

const initials = computed(() => {
  const value = (name.value || "OpenMat").trim();
  return value
    .split(/\s+/)
    .slice(0, 2)
    .map((part) => part[0]?.toUpperCase() || "")
    .join("") || "OM";
});

async function load() {
  const slug = sessionState.me?.practitioner_slug;
  if (!sessionState.token || !slug) return;
  const p = await fetchPublicPractitioner(slug);
  name.value = p.name || "";
  bio.value = p.bio || "";
  avatarUrl.value = p.avatar_url || p.profile_image || "";
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

function editProfile() {
  void router.push({ name: "profile" });
}

onMounted(() => {
  void load();
});
</script>

<style scoped>
.stack { display: grid; gap: 14px; padding-bottom: calc(108px + env(safe-area-inset-bottom, 0px)); }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: 18px; background: rgba(10,20,36,.72); padding: 16px; display: grid; gap: 12px; }
.profile-card { justify-items: center; text-align: center; }
.avatar-wrap { width: 96px; height: 96px; border-radius: 999px; border: 1px solid rgba(255,255,255,.2); overflow: hidden; background: rgba(255,255,255,.06); }
.avatar { width: 100%; height: 100%; object-fit: cover; }
.avatar.fallback { display: grid; place-items: center; font-weight: 700; color: #f4d8a7; height: 100%; }
h1 { margin: 0; font-size: 28px; line-height: 1.05; }
.sub { margin: 0; color: rgba(230,238,249,.75); }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; justify-content: center; }
.btn {
  min-height: 44px;
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.05);
  color: #e8eef8;
  padding: 0 12px;
}
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
</style>
