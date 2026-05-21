<template>
  <article class="deal-card">
    <p class="deal-meta">Profile</p>
    <p class="deal-title">Practitioner bootstrap</p>
    <button
      v-if="sessionState.me && sessionState.me.role === 'practitioner' && !sessionState.me.practitioner_id"
      class="ghost-btn"
      @click="onBootstrap"
    >
      Bootstrap practitioner profile
    </button>
    <p class="subtitle" v-else-if="sessionState.me?.practitioner_id">
      Practitioner linked: {{ sessionState.me.practitioner_name || sessionState.me.practitioner_id }}
    </p>
  </article>
</template>

<script setup lang="ts">
import { bootstrapMe, sessionState } from "../../stores/session";

async function onBootstrap() {
  try {
    await bootstrapMe();
    sessionState.statusText = "Practitioner profile bootstrapped";
  } catch (err) {
    sessionState.statusText = `Bootstrap failed: ${String(err)}`;
  }
}
</script>
