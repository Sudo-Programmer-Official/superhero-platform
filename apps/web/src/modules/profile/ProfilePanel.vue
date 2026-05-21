<template>
  <section class="zone-card-stack">
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
      <p class="subtitle" v-if="sessionState.me?.practitioner_slug">
        Public URL: /openmat/{{ sessionState.me.practitioner_slug }}
      </p>
    </article>

    <article class="deal-card">
      <p class="deal-meta">Redeem Operations</p>
      <p class="deal-title">Manual redeem and restore</p>
      <div class="auth-grid">
        <input v-model="qrCode" class="field" placeholder="QR code" />
        <button class="ghost-btn" @click="onRedeem">Redeem by QR</button>
      </div>
      <div class="auth-grid" v-if="walletPasses.length">
        <button
          v-for="pass in walletPasses"
          :key="pass.id"
          class="ghost-btn"
          @click="onRestore(pass.id)"
        >
          Restore {{ pass.id.slice(0, 8) }} ({{ pass.status }})
        </button>
      </div>
    </article>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

import { listWalletPasses, redeemWalletPass, restoreWalletPass, type WalletPassPayload } from "../../services/api";
import { bootstrapMe, sessionState } from "../../stores/session";

const qrCode = ref("");
const walletPasses = ref<WalletPassPayload[]>([]);

async function onBootstrap() {
  try {
    await bootstrapMe();
    sessionState.statusText = "Practitioner profile bootstrapped";
  } catch (err) {
    sessionState.statusText = `Bootstrap failed: ${String(err)}`;
  }
}

async function loadWalletPasses() {
  if (!sessionState.token) return;
  try {
    walletPasses.value = await listWalletPasses(sessionState.token);
  } catch (err) {
    sessionState.statusText = `Wallet pass load failed: ${String(err)}`;
  }
}

async function onRedeem() {
  if (!sessionState.token || !qrCode.value) return;
  try {
    await redeemWalletPass(sessionState.token, qrCode.value);
    sessionState.statusText = "Wallet pass redeemed";
    qrCode.value = "";
    await loadWalletPasses();
  } catch (err) {
    sessionState.statusText = `Redeem failed: ${String(err)}`;
  }
}

async function onRestore(walletPassId: string) {
  if (!sessionState.token) return;
  try {
    await restoreWalletPass(sessionState.token, walletPassId);
    sessionState.statusText = "Wallet pass restored";
    await loadWalletPasses();
  } catch (err) {
    sessionState.statusText = `Restore failed: ${String(err)}`;
  }
}

onMounted(loadWalletPasses);
</script>
