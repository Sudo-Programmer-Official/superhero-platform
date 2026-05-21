<template>
  <section class="zone zone-card-stack">
    <article class="deal-card">
      <p class="deal-meta">Public Profile</p>
      <p class="deal-title">{{ practitioner?.name || practitionerSlug }}</p>
      <p class="subtitle">{{ practitioner?.bio || "Published and expired experiences" }}</p>
      <p class="subtitle" v-if="practitioner?.location">{{ practitioner.location }}</p>
    </article>

    <article class="deal-card" v-for="deal in deals" :key="deal.id">
      <p class="deal-meta">{{ deal.status.toUpperCase() }}</p>
      <p class="deal-title">{{ deal.title }}</p>
      <p class="subtitle">{{ deal.location }} · {{ new Date(deal.start_time).toLocaleString() }}</p>
      <p class="deal-price">${{ deal.price }}</p>
      <RouterLink class="ghost-btn" :to="`/openmat/${practitionerSlug}/${deal.slug}`">Open deal</RouterLink>
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

onMounted(load);
</script>
