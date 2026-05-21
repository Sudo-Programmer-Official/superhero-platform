<template>
  <section class="zone zone-card-stack">
    <article class="deal-card" v-if="deal">
      <p class="deal-meta">{{ deal.status.toUpperCase() }}</p>
      <p class="deal-title">{{ deal.title }}</p>
      <p class="subtitle">{{ deal.description || "Wellness experience" }}</p>
      <p class="subtitle">{{ deal.location }} · {{ new Date(deal.start_time).toLocaleString() }}</p>
      <p class="deal-price">${{ deal.price }}</p>
      <button class="ghost-btn" :disabled="deal.status !== 'published'" @click="onCheckout">
        {{ deal.status === "published" ? (deal.cta_text || "Book now") : "Unavailable" }}
      </button>
    </article>
    <article class="deal-card muted" v-if="statusText">
      <p class="deal-meta">Status</p>
      <p class="deal-title">{{ statusText }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import { createCheckoutSession, fetchPublicDeal, type DealCardPayload } from "../services/api";

const route = useRoute();
const deal = ref<DealCardPayload | null>(null);
const statusText = ref("");

async function load() {
  const practitionerSlug = String(route.params.practitionerSlug || "");
  const dealSlug = String(route.params.dealSlug || "");
  if (!practitionerSlug || !dealSlug) return;
  try {
    deal.value = await fetchPublicDeal(practitionerSlug, dealSlug);
  } catch (err) {
    statusText.value = `Failed to load deal: ${String(err)}`;
  }
}

async function onCheckout() {
  if (!deal.value) return;
  try {
    const res = await createCheckoutSession({
      deal_id: deal.value.id,
      customer_email: "guest@example.com",
      customer_name: "Guest Customer",
      success_url: `${window.location.origin}${window.location.pathname}?checkout=success`,
      cancel_url: `${window.location.origin}${window.location.pathname}?checkout=cancel`
    });
    window.location.href = res.checkout_url;
  } catch (err) {
    statusText.value = `Checkout failed: ${String(err)}`;
  }
}

onMounted(load);
</script>
