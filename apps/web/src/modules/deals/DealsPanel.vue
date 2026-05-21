<template>
  <section class="zone-card-stack">
    <article class="deal-card">
      <p class="deal-meta">Create Deal</p>
      <p class="deal-title">Publish in under 3 minutes</p>
      <div class="auth-grid">
        <input v-model="form.title" class="field" placeholder="Deal title" />
        <input v-model="form.description" class="field" placeholder="Short description" />
        <input v-model="form.location" class="field" placeholder="Location" />
        <input v-model="form.image" class="field" placeholder="Cover image URL" />
        <input v-model="form.price" class="field" type="number" min="0" step="0.01" placeholder="Price (USD)" />
        <input v-model.number="form.capacity" class="field" type="number" min="1" placeholder="Capacity" />
        <input v-model="form.cta_text" class="field" placeholder="CTA text (Book now)" />
        <input v-model="form.booking_url" class="field" placeholder="External booking URL" />
        <label class="deal-meta">Start time</label>
        <input v-model="form.start_time" class="field" type="datetime-local" />
        <label class="deal-meta">End time</label>
        <input v-model="form.end_time" class="field" type="datetime-local" />
        <button class="ghost-btn" @click="onCreateDeal">Create draft</button>
      </div>
    </article>

    <article class="deal-card muted" v-if="sessionState.statusText">
      <p class="deal-meta">Status</p>
      <p class="deal-title">{{ sessionState.statusText }}</p>
    </article>

    <article class="deal-card" v-for="deal in deals" :key="deal.id">
      <p class="deal-meta">{{ deal.status.toUpperCase() }}</p>
      <p class="deal-title">{{ deal.title }}</p>
      <p class="subtitle">{{ deal.location }} · {{ prettyDate(deal.start_time) }}</p>
      <p class="deal-price">${{ deal.price }}</p>
      <div class="auth-grid">
        <button v-if="deal.status !== 'published'" class="ghost-btn" @click="onPublish(deal.id)">Publish</button>
        <button v-if="deal.status !== 'expired'" class="ghost-btn" @click="onExpire(deal.id)">Mark expired</button>
        <button v-if="deal.share_link" class="ghost-btn" @click="onCopyShare(deal.share_link)">Copy share path</button>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";

import { createDeal, listDeals, type DealCardPayload, updateDealStatus } from "../../services/api";
import { sessionState } from "../../stores/session";

const deals = ref<DealCardPayload[]>([]);
const form = reactive({
  title: "",
  description: "",
  location: "",
  image: "",
  price: "25.00",
  capacity: 20,
  cta_text: "Book now",
  booking_url: "",
  start_time: "",
  end_time: ""
});

function prettyDate(value: string): string {
  const date = new Date(value);
  return date.toLocaleString();
}

async function loadDeals() {
  if (!sessionState.token) return;
  try {
    deals.value = await listDeals(sessionState.token);
  } catch (err) {
    sessionState.statusText = `Failed to load deals: ${String(err)}`;
  }
}

async function onCreateDeal() {
  if (!sessionState.token || !sessionState.me?.practitioner_id) return;
  try {
    await createDeal(sessionState.token, {
      practitioner_id: sessionState.me.practitioner_id,
      title: form.title,
      description: form.description || null,
      location: form.location,
      image: form.image || null,
      price: form.price,
      capacity: form.capacity,
      cta_text: form.cta_text || null,
      booking_url: form.booking_url || null,
      start_time: new Date(form.start_time).toISOString(),
      end_time: new Date(form.end_time).toISOString()
    });
    sessionState.statusText = "Draft created";
    await loadDeals();
  } catch (err) {
    sessionState.statusText = `Create failed: ${String(err)}`;
  }
}

async function onPublish(dealId: string) {
  if (!sessionState.token) return;
  try {
    await updateDealStatus(sessionState.token, dealId, "published");
    sessionState.statusText = "Deal published";
    await loadDeals();
  } catch (err) {
    sessionState.statusText = `Publish failed: ${String(err)}`;
  }
}

async function onExpire(dealId: string) {
  if (!sessionState.token) return;
  try {
    await updateDealStatus(sessionState.token, dealId, "expired");
    sessionState.statusText = "Deal marked expired";
    await loadDeals();
  } catch (err) {
    sessionState.statusText = `Expire failed: ${String(err)}`;
  }
}

async function onCopyShare(sharePath: string) {
  await navigator.clipboard.writeText(`${window.location.origin}${sharePath}`);
  sessionState.statusText = "Share link copied";
}

onMounted(async () => {
  await loadDeals();
});
</script>
