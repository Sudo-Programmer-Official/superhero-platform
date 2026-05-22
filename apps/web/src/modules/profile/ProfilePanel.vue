<template>
  <section class="grid gap-3">
    <DealCardPattern>
      <template #meta>Profile</template>
      <template #title>Practitioner bootstrap</template>
      <template #actions>
        <AppButton
          v-if="sessionState.me && sessionState.me.role === 'practitioner' && !sessionState.me.practitioner_id"
          variant="primary"
          @click="onBootstrap"
        >
          Bootstrap practitioner profile
        </AppButton>
      </template>
      <template #subtitle>
        <span v-if="sessionState.me?.practitioner_id">
          Practitioner linked: {{ sessionState.me.practitioner_name || sessionState.me.practitioner_id }}
        </span>
        <br v-if="sessionState.me?.practitioner_id && sessionState.me?.practitioner_slug" />
        <span v-if="sessionState.me?.practitioner_slug">
          Public URL: /openmat/{{ sessionState.me.practitioner_slug }}
        </span>
      </template>
    </DealCardPattern>

    <DealCardPattern>
      <template #meta>Redeem Operations</template>
      <template #title>Manual redeem and restore</template>
      <template #actions>
        <div class="grid gap-2">
          <AppInput v-model="qrCode" placeholder="QR code" />
          <AppButton @click="onRedeem">Redeem by QR</AppButton>
        </div>
        <div class="grid gap-2" v-if="walletPasses.length">
          <AppButton
            v-for="pass in walletPasses"
            :key="pass.id"
            @click="onRestore(pass.id)"
          >
            Restore {{ pass.id.slice(0, 8) }} ({{ pass.status }})
          </AppButton>
        </div>
      </template>
    </DealCardPattern>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

import DealCardPattern from "../../design-system/patterns/DealCardPattern.vue";
import AppButton from "../../design-system/primitives/AppButton.vue";
import AppInput from "../../design-system/primitives/AppInput.vue";
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
