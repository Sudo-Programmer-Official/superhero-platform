<template>
  <section class="onboarding">
    <BaseGlassCard class="onboarding__card" variant="auth">
      <div class="onboarding__inner">
        <p class="onboarding__label">Onboarding</p>
        <h1 class="onboarding__title">Set up your profile</h1>
        <p class="onboarding__subtitle">Complete this once to unlock your dashboard.</p>

        <div v-if="errorMessage" class="onboarding__error" role="alert">{{ errorMessage }}</div>

        <div class="onboarding__group">
          <p class="onboarding__field-label">Display name</p>
          <AppInput v-model="displayName" placeholder="Your name" icon="✦" />
        </div>

        <div class="onboarding__group">
          <p class="onboarding__field-label">Practice name</p>
          <AppInput v-model="practiceName" placeholder="Your practice name" icon="✦" />
        </div>

        <div class="onboarding__group">
          <p class="onboarding__field-label">Category</p>
          <AppInput v-model="category" placeholder="e.g. Sports therapy" icon="#" />
        </div>

        <div class="onboarding__group">
          <p class="onboarding__field-label">Location</p>
          <AppInput v-model="location" placeholder="City, State" icon="⌖" />
        </div>

        <div class="onboarding__group">
          <p class="onboarding__field-label">Avatar URL</p>
          <AppInput v-model="avatarUrl" placeholder="https://..." icon="◌" />
        </div>

        <AppButton class="onboarding__cta" variant="primary" size="form" :disabled="isSubmitting" @click="onContinue">
          {{ isSubmitting ? "Saving profile..." : "Continue to dashboard" }}
        </AppButton>
      </div>
    </BaseGlassCard>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppInput from "../design-system/primitives/AppInput.vue";
import BaseGlassCard from "../design-system/primitives/BaseGlassCard.vue";
import { updateCurrentUserProfile } from "../firebase/auth";
import { updatePractitioner } from "../services/api";
import { bootstrapMe, refreshMe, sessionState } from "../stores/session";

const router = useRouter();
const displayName = ref(sessionState.user?.displayName || "");
const practiceName = ref(sessionState.me?.practitioner_name || "");
const category = ref("");
const location = ref("");
const avatarUrl = ref("");
const errorMessage = ref("");
const isSubmitting = ref(false);

async function onContinue() {
  if (isSubmitting.value) return;
  errorMessage.value = "";

  if (!practiceName.value.trim()) {
    errorMessage.value = "Practice name is required.";
    return;
  }
  if (!displayName.value.trim()) {
    errorMessage.value = "Display name is required.";
    return;
  }

  if (!sessionState.token) {
    await router.push("/signin");
    return;
  }

  isSubmitting.value = true;
  try {
    await updateCurrentUserProfile(displayName.value.trim(), avatarUrl.value.trim() || null);
    await bootstrapMe(practiceName.value.trim());
    await refreshMe();

    if (sessionState.me?.practitioner_id) {
      await updatePractitioner(sessionState.token, sessionState.me.practitioner_id, {
        name: practiceName.value.trim(),
        bio: category.value.trim() || null,
        location: location.value.trim() || null,
        profile_image: avatarUrl.value.trim() || null
      });
      await refreshMe();
    }

    await router.push("/dashboard");
  } catch (err) {
    errorMessage.value = `Could not complete onboarding: ${String(err)}`;
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.onboarding {
  display: flex;
  justify-content: center;
}

.onboarding__card {
  width: 100%;
  max-width: 560px;
}

.onboarding__inner {
  padding: 32px;
}

.onboarding__label {
  margin: 0;
  color: var(--accent);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.onboarding__title {
  margin: 14px 0 10px;
  font-size: 34px;
  line-height: 1;
}

.onboarding__subtitle {
  margin: 0 0 20px;
  color: rgba(255, 255, 255, 0.68);
}

.onboarding__group {
  margin-bottom: 16px;
}

.onboarding__field-label {
  margin: 0 0 12px;
  color: rgba(255, 255, 255, 0.66);
  font-size: 12px;
}

.onboarding__error {
  margin-bottom: 16px;
  border: 1px solid rgba(255, 106, 106, 0.55);
  background: rgba(255, 106, 106, 0.13);
  border-radius: 12px;
  padding: 10px 12px;
  color: #ffd0d0;
  font-size: 13px;
}

.onboarding__cta {
  width: 100%;
  margin-top: 8px;
}
</style>
