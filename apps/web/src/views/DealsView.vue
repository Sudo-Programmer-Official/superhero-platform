<template>
  <section class="mx-auto grid w-full max-w-screen-xl gap-3 px-4 pb-24 pt-6 sm:px-6 lg:px-2">
    <div class="flex items-center justify-between">
      <h1 class="m-0 text-2xl font-bold tracking-[-0.02em]">Deals</h1>
      <AppButton tag="RouterLink" to="/dashboard/deals/create" variant="primary" size="form">Create Deal</AppButton>
    </div>
    <DealsPanel />
  </section>
</template>

<script setup lang="ts">
import AppButton from "../design-system/primitives/AppButton.vue";
import DealsPanel from "../modules/deals/DealsPanel.vue";
</script>
