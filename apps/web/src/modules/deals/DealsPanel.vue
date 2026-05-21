<template>
  <article class="deal-card">
    <p class="deal-meta">Authenticated</p>
    <p class="deal-title">{{ sessionState.user?.email || "Signed in user" }}</p>
    <p class="deal-price">Role: {{ sessionState.me?.role || "loading" }}</p>
  </article>
</template>

<script setup lang="ts">
import { sessionState } from "../../stores/session";
</script>
