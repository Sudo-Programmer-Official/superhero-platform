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
          <p class="eyebrow">Offers</p>
          <h2>More active offers</h2>
        </div>
      </div>
      <div v-if="loading" class="skeleton-list">
        <div v-for="n in 2" :key="n" class="skeleton shimmer"></div>
      </div>
      <p v-else-if="errorText" class="hint is-error">{{ errorText }}</p>
      <div v-else-if="publishedDeals.length" class="offers">
        <article v-for="deal in publishedDeals" :key="deal.id" class="offer-row" :class="{ active: primaryOffer?.id === deal.id }">
          <div class="offer-copy">
            <p class="title">{{ deal.title }}</p>
            <p class="hint">{{ formatDate(deal.start_time) }}</p>
          </div>
          <div class="offer-actions">
            <button class="btn" type="button" @click="setActiveDeal(deal.id)" :disabled="primaryOffer?.id === deal.id">
              {{ primaryOffer?.id === deal.id ? "Active" : "Set Active" }}
            </button>
            <button class="btn" @click="copyOfferLink(deal.slug)">Copy</button>
          </div>
        </article>
      </div>
      <p v-else class="hint">No published offers yet.</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { formatLocalDateTime, formatMoney } from "../../domain/deal";
import {
  listDeals,
  type DealCardPayload
} from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

const router = useRouter();
const loading = ref(false);
const errorText = ref("");
const deals = ref<DealCardPayload[]>([]);
const activeDealId = ref<string | null>(null);

const publishedDeals = computed(() => deals.value.filter((d) => d.status === "published"));
const primaryOffer = computed(() => {
  if (!publishedDeals.value.length) return null;
  if (activeDealId.value) {
    const selected = publishedDeals.value.find((d) => d.id === activeDealId.value);
    if (selected) return selected;
  }
  return publishedDeals.value[0] || null;
});

function formatDate(value: string): string {
  return formatLocalDateTime(value, "UTC");
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
    const storedActiveId = window.localStorage.getItem("openmat_active_deal_id");
    if (storedActiveId) activeDealId.value = storedActiveId;
  } catch (err) {
    errorText.value = `Failed to load share data: ${String(err)}`;
  } finally {
    loading.value = false;
  }
}

function setActiveDeal(dealId: string) {
  activeDealId.value = dealId;
  window.localStorage.setItem("openmat_active_deal_id", dealId);
  showToast("Active deal updated.", "success");
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
  void router.push({ name: "app-deals-create" });
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
.row, .hero-actions { display: flex; gap: 8px; flex-wrap: wrap; }
.btn { min-height: var(--mvp-btn-h, 44px); border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; }
.btn:disabled { opacity: .5; }
.head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.hint { margin: 0; color: rgba(230,238,249,.72); font-size: 13px; }
.hint.is-error { color: #ffb2b2; }
.offers { display: grid; gap: 8px; }
.offer-row { border: 1px solid rgba(255,255,255,.1); border-radius: 12px; background: rgba(8,14,24,.72); padding: 10px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.offer-row.active { border-color: rgba(240,190,100,.36); box-shadow: 0 0 0 1px rgba(240,190,100,.14) inset; }
.offer-copy { min-width: 0; display: grid; gap: 4px; }
.offer-actions { display: flex; gap: 8px; align-items: center; }
.title { margin: 0; font-weight: 650; }
.skeleton-list { display: grid; gap: 8px; }
.skeleton { height: 80px; border-radius: 12px; border: 1px solid rgba(255,255,255,.08); background: rgba(255,255,255,.04); }
.shimmer { background-image: linear-gradient(100deg, rgba(255,255,255,.03) 20%, rgba(255,255,255,.1) 50%, rgba(255,255,255,.03) 80%); background-size: 200% 100%; animation: shimmer 1.5s linear infinite; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>
