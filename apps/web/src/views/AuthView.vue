<template>
  <section class="zone zone-card-stack">
    <AuthPanel />
    <article class="deal-card muted" v-if="sessionState.statusText">
      <p class="deal-meta">Status</p>
      <p class="deal-title">{{ sessionState.statusText }}</p>
    </article>
  </section>
</template>

<script setup lang="ts">
import AuthPanel from "../modules/auth/AuthPanel.vue";
import { sessionState } from "../stores/session";
</script>
