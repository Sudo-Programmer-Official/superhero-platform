<template>
  <section class="stack">
    <article class="card top">
      <p class="eyebrow">Deals</p>
      <h1>Chronological feed</h1>
      <p class="sub">Most recent offer stays on top. Share directly from each card.</p>
      <button class="btn primary" type="button" @click="createOffer">Create New Deal</button>
    </article>

    <div v-if="loading" class="skeleton-list">
      <div v-for="n in 3" :key="n" class="skeleton shimmer"></div>
    </div>
    <p v-else-if="errorText" class="hint is-error">{{ errorText }}</p>

    <article v-for="(deal, index) in feedDeals" :key="deal.id" class="card deal-card" :class="{ topdeal: index === 0 }">
      <img v-if="deal.image" :src="deal.image" alt="Deal image" class="cover" />
      <div v-else class="cover fallback"></div>
      <div class="body">
        <p class="title">{{ deal.title }}</p>
        <p class="meta">{{ formatDate(deal.start_time) }}<span v-if="deal.location"> · {{ deal.location }}</span></p>
        <p class="meta">{{ formatMoney(deal.base_price, deal.currency) }} · {{ deal.remaining_slots }}/{{ deal.capacity }} left</p>
      </div>
      <div class="actions">
        <button class="btn" type="button" @click="shareOffer(deal.slug)">Share</button>
        <button class="btn" type="button" @click="previewOffer(deal.slug)">Preview</button>
        <details class="overflow">
          <summary aria-label="More actions">•••</summary>
          <div class="overflow-menu">
            <button class="menu-btn" type="button" @click="copyOfferLink(deal.slug)">Copy link</button>
          </div>
        </details>
      </div>
    </article>

    <article v-if="feedDeals.length < 3" class="card create-next">
      <p class="eyebrow">Next</p>
      <h2>Create your next deal</h2>
      <p class="sub">Keep the feed active with a new offer.</p>
      <button class="btn primary" type="button" @click="createOffer">Create Offer</button>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { formatLocalDateTime, formatMoney } from "../../domain/deal";
import { listDeals, type DealCardPayload } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

const router = useRouter();
const loading = ref(false);
const errorText = ref("");
const deals = ref<DealCardPayload[]>([]);

const publishedDeals = computed(() =>
  deals.value
    .filter((d) => d.status === "published")
    .sort((a, b) => new Date(b.start_time).getTime() - new Date(a.start_time).getTime())
);
const feedDeals = computed(() => publishedDeals.value.slice(0, 3));
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
  } catch (err) {
    errorText.value = `Failed to load deals: ${String(err)}`;
  } finally {
    loading.value = false;
  }
}

function createOffer() {
  void router.push({ name: "app-deals-create" });
}

async function copyOfferLink(slug: string) {
  await navigator.clipboard.writeText(offerPath(slug));
  showToast("Offer link copied.", "success");
}

async function shareOffer(slug: string) {
  const url = offerPath(slug);
  if (navigator.share) {
    await navigator.share({ title: "OpenMat offer", url });
  } else {
    await navigator.clipboard.writeText(url);
    showToast("Offer link copied.", "success");
  }
}

function previewOffer(slug: string) {
  window.open(offerPath(slug), "_blank", "noopener,noreferrer");
}

onMounted(() => {
  void load();
});
</script>

<style scoped>
.stack { display: grid; gap: var(--mvp-gap, 14px); padding-bottom: 80px; }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: var(--mvp-radius, 16px); background: rgba(10, 20, 36, .72); padding: var(--mvp-card-pad, 16px); display: grid; gap: 12px; }
.top { background: linear-gradient(170deg, rgba(17, 37, 66, .9), rgba(9, 17, 30, .86)); }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
h1 { margin: 0; font-size: 28px; line-height: 1.06; letter-spacing: -0.02em; }
.sub { margin: 0; color: rgba(230,238,249,.78); }
.deal-card { padding: 0; overflow: hidden; }
.cover { width: 100%; height: 170px; object-fit: cover; display: block; }
.cover.fallback { background: linear-gradient(135deg, rgba(26,42,69,.8), rgba(8,13,24,.95)); }
.body { padding: 12px 14px 0 14px; display: grid; gap: 4px; }
.title { margin: 0; font-size: 23px; font-weight: 700; }
.meta { margin: 0; font-size: 13px; color: rgba(230,238,249,.72); }
.actions { padding: 12px 14px 14px 14px; display: flex; gap: 8px; flex-wrap: wrap; }
.overflow { position: relative; }
.overflow summary {
  list-style: none;
  min-width: 44px;
  min-height: var(--mvp-btn-h, 44px);
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.05);
  color: #e8eef8;
  display: grid;
  place-items: center;
  cursor: pointer;
}
.overflow summary::-webkit-details-marker { display: none; }
.overflow-menu {
  position: absolute;
  right: 0;
  top: calc(100% + 6px);
  width: 150px;
  border-radius: 10px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(8,14,24,.96);
  padding: 6px;
  z-index: 3;
}
.menu-btn {
  width: 100%;
  min-height: 38px;
  border-radius: 8px;
  border: 1px solid rgba(255,255,255,.1);
  background: rgba(255,255,255,.04);
  color: #e8eef8;
  text-align: left;
  padding: 0 10px;
}
.btn { min-height: var(--mvp-btn-h, 44px); border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; width: fit-content; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.deal-card.topdeal { border-color: rgba(240,190,100,.3); box-shadow: 0 0 0 1px rgba(240,190,100,.1) inset; }
.create-next h2 { margin: 0; font-size: 22px; }
.hint { margin: 0; color: rgba(230,238,249,.72); font-size: 13px; }
.hint.is-error { color: #ffb2b2; }
.skeleton-list { display: grid; gap: 8px; }
.skeleton { height: 210px; border-radius: 12px; border: 1px solid rgba(255,255,255,.08); background: rgba(255,255,255,.04); }
.shimmer { background-image: linear-gradient(100deg, rgba(255,255,255,.03) 20%, rgba(255,255,255,.1) 50%, rgba(255,255,255,.03) 80%); background-size: 200% 100%; animation: shimmer 1.5s linear infinite; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>
