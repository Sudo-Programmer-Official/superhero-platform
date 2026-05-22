<template>
  <section class="mx-auto grid w-full max-w-[760px] gap-4 px-4 pb-[calc(8.5rem+var(--safe-bottom))] pt-6 sm:px-6">
    <article
      v-if="deal"
      class="overflow-hidden rounded-[var(--radius-xl)] border border-[color:var(--card-border)] bg-[#f1f3f7] text-[#111827] shadow-[var(--shadow-soft)]"
    >
      <img
        v-if="deal.image"
        :src="deal.image"
        alt="Deal cover"
        class="h-48 w-full object-cover sm:h-56"
      />
      <div v-else class="h-48 w-full bg-[linear-gradient(135deg,#263750,#0d1728)] sm:h-56"></div>
      <div class="grid gap-2 p-4">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="m-0 text-[11px] uppercase tracking-[0.12em] text-[#6b7280]">{{ deal.status.toUpperCase() }}</p>
            <h1 class="m-0 mt-1 text-3xl font-bold leading-tight">{{ deal.title }}</h1>
          </div>
          <p class="m-0 rounded-xl border border-[#d0d5dd] bg-white px-3 py-1 text-xl font-semibold">${{ deal.price }}</p>
        </div>
        <p class="m-0 text-base leading-relaxed text-[#4b5563]">{{ deal.description || "Wellness experience" }}</p>
        <p class="m-0 text-sm text-[#6b7280]">{{ deal.location }} · {{ new Date(deal.start_time).toLocaleString() }}</p>
      </div>
    </article>
    <AppCard v-if="statusText" muted>
      <p class="mb-1 text-xs text-[#9db2d4]">Status</p>
      <p class="m-0 text-sm text-[var(--text-1)]">{{ statusText }}</p>
    </AppCard>

    <div v-if="deal" class="fixed inset-x-0 bottom-0 z-30 border-t border-[color:var(--card-border)] bg-[rgba(11,18,30,.86)] px-4 pb-[calc(.75rem+var(--safe-bottom))] pt-3 backdrop-blur-xl">
      <div class="mx-auto grid w-full max-w-[760px] gap-2">
        <AppButton
          variant="primary"
          size="lg"
          :disabled="deal.status !== 'published'"
          @click="onCheckout"
        >
          {{ deal.status === "published" ? (deal.cta_text || "Book now") : "Unavailable" }}
        </AppButton>
        <AppButton size="lg" @click="onCopyDeal">Copy link</AppButton>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import { createCheckoutSession, fetchPublicDeal, type DealCardPayload } from "../services/api";

const route = useRoute();
const deal = ref<DealCardPayload | null>(null);
const statusText = ref("");
const checkoutTriggered = ref(false);

async function load() {
  const practitionerSlug = String(route.params.practitionerSlug || "");
  const dealSlug = String(route.params.dealSlug || "");
  if (!practitionerSlug || !dealSlug) return;
  try {
    deal.value = await fetchPublicDeal(practitionerSlug, dealSlug);
    const shouldAutoCheckout = String(route.query.autocheckout || "") === "1";
    if (shouldAutoCheckout && deal.value.status === "published" && !checkoutTriggered.value) {
      checkoutTriggered.value = true;
      await onCheckout();
    }
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

async function onCopyDeal() {
  await navigator.clipboard.writeText(window.location.href.split("?")[0] ?? window.location.href);
  statusText.value = "Deal link copied";
}

onMounted(load);
</script>
