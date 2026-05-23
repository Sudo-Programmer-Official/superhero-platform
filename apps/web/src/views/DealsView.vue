<template>
  <DashboardPageShell
    eyebrow="Campaigns"
    title="Deals"
    subtitle="Operate all campaigns from one control surface with consistent filtering, sorting, and actions."
  >
    <template #actions>
      <AppButton tag="RouterLink" to="/dashboard/deals/create" variant="primary" size="form">Create Deal</AppButton>
    </template>

    <DealsPanel :focus-deal-id="focusDealId" />
  </DashboardPageShell>
</template>

<script setup lang="ts">
import { computed } from "vue";
import { useRoute } from "vue-router";
import DashboardPageShell from "../design-system/patterns/DashboardPageShell.vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import DealsPanel from "../modules/deals/DealsPanel.vue";

const route = useRoute();
const focusDealId = computed(() => String(route.query.deal || "").trim() || undefined);
</script>
