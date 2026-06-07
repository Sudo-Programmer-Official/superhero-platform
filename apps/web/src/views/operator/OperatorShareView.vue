<template>
  <section class="stack">
    <article class="card top">
      <p class="eyebrow">Deals</p>
      <h1>Chronological feed</h1>
      <p class="sub">This is the place to post offers and share them fast.</p>
      <button class="btn primary" type="button" @click="createOffer">Create Deal</button>
    </article>

    <div v-if="loading" class="skeleton-list">
      <div v-for="n in 3" :key="n" class="skeleton shimmer"></div>
    </div>
    <p v-else-if="errorText" class="hint is-error">{{ errorText }}</p>

    <article v-for="deal in feedDeals" :key="deal.id" class="card deal-card" :class="{ topdeal: deal.id === feedDeals[0]?.id }">
      <div class="cover-wrap">
        <img v-if="deal.cover" :src="deal.cover" alt="Deal cover" class="cover" />
        <div v-else class="cover cover--fallback"></div>
      </div>

      <div class="body">
        <p class="title">{{ deal.title }}</p>
        <p class="meta">{{ deal.offer }}</p>
        <p class="meta">{{ deal.expiry }} · {{ deal.location }}</p>
        <div class="metrics">
          <span>Claimed {{ deal.claimed }}</span>
          <span>Redeemed {{ deal.redeemed }}</span>
        </div>
      </div>

      <div class="actions">
        <button class="btn" type="button" @click="shareOffer(deal.slug)">Share</button>
        <button class="btn" type="button" @click="previewOffer(deal.slug)">Preview</button>
        <details class="overflow">
          <summary aria-label="More actions">•••</summary>
          <div class="overflow-menu">
            <button class="menu-btn" type="button" @click="copyOfferLink(deal.slug)">Copy link</button>
            <button class="menu-btn menu-btn--danger" type="button" @click="archiveOffer(deal.id)">Archive</button>
          </div>
        </details>
      </div>
    </article>

    <article v-if="feedDeals.length === 0 && !loading && !errorText" class="card empty-card">
      <p class="eyebrow">Start here</p>
      <h2>Post your first offer</h2>
      <p class="sub">Upload a flyer, add the title, and publish to the feed.</p>
      <button class="btn primary" type="button" @click="createOffer">Create Deal</button>
    </article>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref } from "vue";
import { useRouter } from "vue-router";
import { archiveDeal, listDeals, listWalletPasses, type DealCardPayload, type WalletPassPayload } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

type FeedDeal = {
  id: string;
  slug: string;
  cover: string | null;
  title: string;
  offer: string;
  expiry: string;
  location: string;
  claimed: number;
  redeemed: number;
};

const router = useRouter();
const loading = ref(false);
const errorText = ref("");
const deals = ref<DealCardPayload[]>([]);
const walletPasses = ref<WalletPassPayload[]>([]);

const feedDeals = computed<FeedDeal[]>(() => {
  const byDeal = new Map<string, { claimed: number; redeemed: number }>();
  for (const pass of walletPasses.value) {
    const key = pass.deal_id;
    const current = byDeal.get(key) || { claimed: 0, redeemed: 0 };
    current.claimed += 1;
    if ((pass.pass_status || "").toLowerCase() === "redeemed" || (pass.redemption_status || "").toLowerCase() === "redeemed") {
      current.redeemed += 1;
    }
    byDeal.set(key, current);
  }

  return deals.value
    .filter((deal) => deal.status === "published")
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 6)
    .map((deal) => {
      const counts = byDeal.get(deal.id) || { claimed: 0, redeemed: 0 };
      return {
        id: deal.id,
        slug: deal.slug,
        cover: deal.cover_image || deal.image || null,
        title: deal.title,
        offer: deal.description || deal.cta_text || `from ${deal.price} ${deal.currency}`,
        expiry: deal.expiration_time ? `Expires ${new Date(deal.expiration_time).toLocaleDateString()}` : `Expires ${new Date(deal.end_time).toLocaleDateString()}`,
        location: deal.location || deal.location_name || "Location not set",
        claimed: counts.claimed,
        redeemed: counts.redeemed
      };
    });
});

function offerPath(slug: string): string {
  const practitionerSlug = sessionState.me?.practitioner_slug || "";
  return `${window.location.origin}/openmat/${practitionerSlug}/${slug}`;
}

async function load() {
  if (!sessionState.token) return;
  loading.value = true;
  errorText.value = "";
  try {
    const [dealList, passList] = await Promise.all([listDeals(sessionState.token), listWalletPasses(sessionState.token)]);
    deals.value = dealList;
    walletPasses.value = passList;
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

async function archiveOffer(dealId: string) {
  if (!sessionState.token) return;
  try {
    await archiveDeal(sessionState.token, dealId);
    showToast("Offer archived.", "success");
    await load();
  } catch (err) {
    showToast(`Failed to archive offer: ${String(err)}`, "error");
  }
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
  window.addEventListener("focus", handleRefreshVisibility, { passive: true });
  document.addEventListener("visibilitychange", handleRefreshVisibility);
});

onBeforeUnmount(() => {
  window.removeEventListener("focus", handleRefreshVisibility);
  document.removeEventListener("visibilitychange", handleRefreshVisibility);
});

function handleRefreshVisibility() {
  if (document.visibilityState === "visible") {
    void load();
  }
}
</script>

<style scoped>
.stack { display: grid; gap: 14px; padding-bottom: calc(108px + env(safe-area-inset-bottom, 0px)); }
.card { border: 1px solid rgba(255,255,255,.12); border-radius: 18px; background: rgba(10, 20, 36, .72); padding: 16px; display: grid; gap: 12px; }
.top { background: linear-gradient(170deg, rgba(17, 37, 66, .9), rgba(9, 17, 30, .86)); }
.eyebrow { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
h1 { margin: 0; font-size: 28px; line-height: 1.06; letter-spacing: -0.02em; }
.sub { margin: 0; color: rgba(230,238,249,.78); }
.deal-card { padding: 0; overflow: visible; position: relative; }
.cover-wrap { border-radius: 18px 18px 0 0; overflow: hidden; }
.cover { width: 100%; aspect-ratio: 1.15 / 1; object-fit: cover; display: block; }
.cover--fallback { background: radial-gradient(circle at 30% 20%, rgba(240,190,100,.16), transparent 36%), linear-gradient(135deg, rgba(26,42,69,.8), rgba(8,13,24,.95)); }
.body { padding: 12px 14px 0 14px; display: grid; gap: 4px; }
.title { margin: 0; font-size: 23px; font-weight: 700; line-height: 1.06; }
.meta { margin: 0; font-size: 13px; color: rgba(230,238,249,.72); }
.metrics { display: flex; flex-wrap: wrap; gap: 8px; padding-top: 4px; }
.metrics span { border-radius: 999px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.04); color: rgba(233,241,252,.82); padding: 6px 10px; font-size: 12px; }
.actions { padding: 12px 14px 14px 14px; display: flex; gap: 8px; flex-wrap: wrap; position: relative; z-index: 4; }
.overflow { position: relative; }
.overflow summary {
  list-style: none;
  min-width: 44px;
  min-height: 44px;
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
  z-index: 20;
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
.menu-btn--danger { color: #ffb2b2; }
.btn { min-height: 44px; border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.05); color: #e8eef8; padding: 0 12px; }
.btn.primary { border-color: rgba(240,190,100,.46); color: #0c1728; background: linear-gradient(145deg, #f3d89f, #e9c57b); font-weight: 700; width: fit-content; }
.btn:disabled { opacity: .5; cursor: not-allowed; }
.hint { margin: 0; color: rgba(230,238,249,.72); font-size: 13px; }
.hint.is-error { color: #ffb2b2; }
.skeleton-list { display: grid; gap: 8px; }
.skeleton { height: 210px; border-radius: 12px; border: 1px solid rgba(255,255,255,.08); background: rgba(255,255,255,.04); }
.shimmer { background-image: linear-gradient(100deg, rgba(255,255,255,.03) 20%, rgba(255,255,255,.1) 50%, rgba(255,255,255,.03) 80%); background-size: 200% 100%; animation: shimmer 1.5s linear infinite; }
.empty-card h2 { margin: 0; font-size: 22px; }
@keyframes shimmer { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
</style>
