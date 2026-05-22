<template>
  <section class="mx-auto grid w-full max-w-[760px] gap-4 px-4 pb-[calc(8.5rem+var(--safe-bottom))] pt-6 sm:px-6">
    <article class="grid justify-items-center gap-3 rounded-[var(--radius-xl)] border border-[color:var(--card-border)] bg-[rgba(15,24,39,.65)] p-6 text-center shadow-[var(--shadow-soft)]">
      <div class="relative">
        <div class="absolute inset-0 rounded-full bg-[var(--accent-glow)] blur-2xl" aria-hidden="true"></div>
        <img
          v-if="practitioner?.profile_image"
          :src="practitioner.profile_image"
          alt="Profile"
          class="relative h-20 w-20 rounded-full border border-[color:var(--card-border)] object-cover"
        />
        <div v-else class="relative h-20 w-20 rounded-full border border-[color:var(--card-border)] bg-[rgba(22,35,54,.9)]"></div>
      </div>
      <h1 class="m-0 text-3xl font-bold tracking-[-0.01em]">{{ practitioner?.name || practitionerSlug }}</h1>
      <p class="m-0 text-lg text-[var(--text-secondary)]">{{ practitioner?.bio || "Published and expired experiences" }}</p>
      <p v-if="practitioner?.location" class="m-0 text-sm text-[var(--text-muted)]">{{ practitioner.location }}</p>
    </article>

    <article
      v-for="deal in deals"
      :key="deal.id"
      class="overflow-hidden rounded-[var(--radius-xl)] border border-[color:var(--card-border)] bg-[#f1f3f7] text-[#111827] shadow-[var(--shadow-soft)]"
    >
      <img
        v-if="deal.image"
        :src="deal.image"
        alt="Deal cover"
        class="h-44 w-full object-cover sm:h-52"
      />
      <div v-else class="h-44 w-full bg-[linear-gradient(135deg,#263750,#0d1728)] sm:h-52"></div>
      <div class="grid gap-2 p-4">
        <div class="flex items-start justify-between gap-3">
          <div>
            <p class="m-0 text-[11px] uppercase tracking-[0.12em] text-[#6b7280]">{{ deal.status.toUpperCase() }}</p>
            <p class="m-0 mt-1 text-2xl font-bold leading-tight">{{ deal.title }}</p>
          </div>
          <p class="m-0 rounded-xl border border-[#d0d5dd] bg-white px-3 py-1 text-xl font-semibold">${{ deal.price }}</p>
        </div>
        <p class="m-0 text-sm text-[#4b5563]">{{ deal.location_name }} · {{ formatEventTime(deal.start_at, deal.timezone) }}</p>
        <AppButton tag="RouterLink" variant="secondary" size="lg" :to="`/openmat/${practitionerSlug}/${deal.slug}`">Open deal</AppButton>
      </div>
    </article>

    <AppCard v-if="statusText" muted>
      <p class="mb-1 text-xs text-[#9db2d4]">Status</p>
      <p class="m-0 text-sm text-[var(--text-1)]">{{ statusText }}</p>
    </AppCard>

    <div class="fixed inset-x-0 bottom-0 z-30 border-t border-[color:var(--card-border)] bg-[rgba(11,18,30,.86)] px-4 pb-[calc(.75rem+var(--safe-bottom))] pt-3 backdrop-blur-xl">
      <div class="mx-auto grid w-full max-w-[760px] gap-2">
        <AppButton variant="primary" size="lg" @click="onCopyProfile">Copy link</AppButton>
        <AppButton size="lg" @click="onShareProfile">Share</AppButton>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useRoute } from "vue-router";

import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import { formatLocalDateTime, formatTimezone } from "../domain/deal";
import { fetchPublicPractitioner, listPublicDeals, type DealCardPayload, type PractitionerPublicPayload } from "../services/api";

const route = useRoute();
const practitionerSlug = String(route.params.practitionerSlug || "");
const deals = ref<DealCardPayload[]>([]);
const practitioner = ref<PractitionerPublicPayload | null>(null);
const statusText = ref("");

async function load() {
  if (!practitionerSlug) return;
  try {
    practitioner.value = await fetchPublicPractitioner(practitionerSlug);
    deals.value = await listPublicDeals(practitionerSlug);
  } catch (err) {
    statusText.value = `Failed to load profile: ${String(err)}`;
  }
}

function profileUrl(): string {
  return `${window.location.origin}/openmat/${practitionerSlug}`;
}

async function onCopyProfile() {
  await navigator.clipboard.writeText(profileUrl());
  statusText.value = "Profile link copied";
}

async function onShareProfile() {
  const url = profileUrl();
  if (navigator.share) {
    await navigator.share({ title: practitioner.value?.name || "Profile", url });
    return;
  }
  await navigator.clipboard.writeText(url);
  statusText.value = "Profile link copied";
}

onMounted(load);
</script>
function formatEventTime(value: string, timezone: string): string {
  return `${formatLocalDateTime(value, timezone)} ${formatTimezone(value, timezone)}`;
}
