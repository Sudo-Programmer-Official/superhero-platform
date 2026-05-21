<template>
  <section class="zone zone-card-stack">
    <article class="deal-card">
      <p class="deal-meta">Platform Auth</p>
      <p class="deal-title">Firebase + /me bootstrap ready</p>
      <p class="subtitle">Signed in as {{ sessionState.user?.email || "unknown" }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import { sessionState } from "../stores/session";
</script>
