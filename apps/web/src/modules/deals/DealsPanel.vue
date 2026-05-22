<template>
  <section class="grid gap-3">
    <AppCard>
      <p class="eyebrow">Deal Studio</p>
      <h2 class="mt-2 text-xl font-bold tracking-[-0.01em]">Create and publish in under 3 minutes</h2>
      <p class="mt-2 text-sm text-[var(--text-secondary)]">
        Publish one high-conversion offer first. You can share it immediately after publish.
      </p>

      <div class="mt-4 grid gap-3 rounded-xl border border-[color:var(--card-border)] bg-[rgba(12,22,36,.55)] p-4">
        <p class="text-xs uppercase tracking-[0.12em] text-[var(--accent)]">Step 1 • Core Offer</p>
        <div class="grid gap-2 sm:grid-cols-2">
          <AppInput v-model="form.title" placeholder="Deal title" />
          <AppInput v-model="form.location" placeholder="Location" />
        </div>
        <AppInput v-model="form.description" placeholder="Short description" />
        <AppInput v-model="form.image" placeholder="Cover image URL" />
      </div>

      <div class="mt-3 grid gap-3 rounded-xl border border-[color:var(--card-border)] bg-[rgba(12,22,36,.55)] p-4">
        <p class="text-xs uppercase tracking-[0.12em] text-[var(--accent)]">Step 2 • Pricing & Conversion</p>
        <div class="grid gap-2 sm:grid-cols-2">
          <AppInput v-model="form.price" type="number" placeholder="Price (USD)" />
          <AppInput v-model="form.capacityText" type="number" placeholder="Capacity" />
        </div>
        <div class="grid gap-2 sm:grid-cols-2">
          <AppInput v-model="form.cta_text" placeholder="CTA text (Book now)" />
          <AppInput v-model="form.booking_url" placeholder="External booking URL" />
        </div>
      </div>

      <div class="mt-3 grid gap-3 rounded-xl border border-[color:var(--card-border)] bg-[rgba(12,22,36,.55)] p-4">
        <p class="text-xs uppercase tracking-[0.12em] text-[var(--accent)]">Step 3 • Timing</p>
        <div class="grid gap-2 sm:grid-cols-2">
          <div class="grid gap-1">
            <label class="text-xs text-[var(--text-muted)]">Start time</label>
            <AppInput v-model="form.start_time" type="datetime-local" />
          </div>
          <div class="grid gap-1">
            <label class="text-xs text-[var(--text-muted)]">End time</label>
            <AppInput v-model="form.end_time" type="datetime-local" />
          </div>
        </div>
      </div>

      <div class="mt-4 flex flex-wrap gap-2">
        <AppButton variant="primary" @click="onCreateDeal">Create draft</AppButton>
        <p class="self-center text-xs text-[var(--text-muted)]">Draft → Publish → Share link</p>
      </div>
    </AppCard>

    <AppCard v-if="sessionState.statusText" :muted="true">
      <p class="mb-1 text-xs uppercase tracking-[0.12em] text-[var(--accent)]">Status</p>
      <p class="m-0 text-sm text-[var(--text-secondary)]">{{ sessionState.statusText }}</p>
    </AppCard>

    <DealCardPattern v-for="deal in deals" :key="deal.id">
      <template #meta>{{ deal.status.toUpperCase() }}</template>
      <template #title>{{ deal.title }}</template>
      <template #subtitle>{{ deal.location }} · {{ prettyDate(deal.start_time) }}</template>
      <template #price>${{ deal.price }}</template>
      <template #actions>
        <AppButton v-if="deal.status !== 'published'" variant="primary" @click="onPublish(deal.id)">Publish</AppButton>
        <AppButton v-if="deal.status !== 'expired'" @click="onExpire(deal.id)">Mark expired</AppButton>
        <AppButton v-if="deal.share_link" @click="onCopyShare(deal.share_link)">Copy share link</AppButton>
        <AppButton v-if="deal.share_link" variant="secondary" @click="onOpenShare(deal.share_link)">Open public page</AppButton>
        <AppButton
          v-if="deal.share_link && deal.status === 'published'"
          variant="primary"
          @click="onTestCheckout(deal.share_link)"
        >
          Test checkout
        </AppButton>
      </template>
    </DealCardPattern>
  </section>
</template>

<script setup lang="ts">
import { onMounted, reactive, ref } from "vue";

import DealCardPattern from "../../design-system/patterns/DealCardPattern.vue";
import AppButton from "../../design-system/primitives/AppButton.vue";
import AppCard from "../../design-system/primitives/AppCard.vue";
import AppInput from "../../design-system/primitives/AppInput.vue";
import { createDeal, listDeals, type DealCardPayload, updateDealStatus } from "../../services/api";
import { sessionState } from "../../stores/session";

const deals = ref<DealCardPayload[]>([]);
const form = reactive({
  title: "",
  description: "",
  location: "",
  image: "",
  price: "25.00",
  capacityText: "20",
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
  if (!form.title || !form.location || !form.start_time || !form.end_time) {
    sessionState.statusText = "Title, location, start, and end time are required";
    return;
  }
  try {
    await createDeal(sessionState.token, {
      practitioner_id: sessionState.me.practitioner_id,
      title: form.title,
      description: form.description || null,
      location: form.location,
      image: form.image || null,
      price: form.price,
      capacity: Number(form.capacityText || 0),
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
  await navigator.clipboard.writeText(toAbsoluteShareUrl(sharePath));
  sessionState.statusText = "Share link copied";
}

function toAbsoluteShareUrl(sharePath: string): string {
  return `${window.location.origin}${sharePath}`;
}

function onOpenShare(sharePath: string) {
  window.open(toAbsoluteShareUrl(sharePath), "_blank", "noopener,noreferrer");
}

function onTestCheckout(sharePath: string) {
  const url = new URL(toAbsoluteShareUrl(sharePath), window.location.origin);
  url.searchParams.set("autocheckout", "1");
  window.open(url.toString(), "_blank", "noopener,noreferrer");
}

onMounted(async () => {
  await loadDeals();
});
</script>
