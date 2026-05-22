<template>
  <BaseGlassCard class="auth-card" variant="auth">
    <div class="auth-card__inner">
      <p class="auth-card__label">Auth · {{ isSignup ? "Sign up" : "Sign in" }}</p>
      <h2 class="auth-card__title">{{ isSignup ? "Create account" : "Welcome back" }}</h2>
      <p class="auth-card__subtitle">{{ isSignup ? "Start your practitioner workspace." : "Sign in to your practitioner account." }}</p>

      <div v-if="errorMessage" class="auth-card__error" role="alert">{{ errorMessage }}</div>

      <div v-if="isSignup" class="auth-card__group">
        <p class="auth-card__field-label">Full name</p>
        <AppInput v-model="name" placeholder="Enter your name" icon="✦" />
      </div>

      <div class="auth-card__group">
        <p class="auth-card__field-label">Email address</p>
        <AppInput v-model="email" placeholder="Enter your email" icon="@" />
      </div>

      <div class="auth-card__group">
        <p class="auth-card__field-label">Password</p>
        <AppInput v-model="password" placeholder="Enter your password" type="password" icon="•" />
      </div>

      <AppButton class="auth-card__cta" variant="primary" size="form" :disabled="isSubmitting" @click="onSubmit">
        {{ isSubmitting ? (isSignup ? "Creating account..." : "Signing in...") : (isSignup ? "Create account" : "Sign in") }}
      </AppButton>

      <p class="auth-card__footer" v-if="isSignup">
        Already have an account?
        <RouterLink to="/signin">Sign in</RouterLink>
      </p>
      <p class="auth-card__footer" v-else>
        Don't have an account?
        <RouterLink to="/signup">Create one</RouterLink>
      </p>
    </div>
  </BaseGlassCard>
</template>

<script setup lang="ts">
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { FirebaseError } from "firebase/app";
import AppButton from "../../design-system/primitives/AppButton.vue";
import AppInput from "../../design-system/primitives/AppInput.vue";
import BaseGlassCard from "../../design-system/primitives/BaseGlassCard.vue";
import { loginWithEmail, signupWithEmail } from "../../firebase/auth";

const props = withDefaults(
  defineProps<{
    mode?: "signin" | "signup";
  }>(),
  {
    mode: "signin"
  }
);

const router = useRouter();
const name = ref("");
const email = ref("");
const password = ref("");
const errorMessage = ref("");
const isSubmitting = ref(false);
const isSignup = computed(() => props.mode === "signup");

function mapAuthError(err: unknown): string {
  if (err instanceof Error) {
    if (err.message.includes("Firebase config missing")) {
      return "Auth is not configured. Add VITE_FIREBASE_* values to apps/web/.env.local and restart dev server.";
    }
    if (err.message.includes("Firebase auth failed to initialize")) {
      return "Firebase auth could not initialize. Verify your Firebase web config values.";
    }
  }
  if (!(err instanceof FirebaseError)) return "Something went wrong. Please try again.";
  switch (err.code) {
    case "auth/invalid-email":
      return "Enter a valid email address.";
    case "auth/weak-password":
      return "Password must be at least 6 characters.";
    case "auth/email-already-in-use":
      return "An account with this email already exists.";
    case "auth/wrong-password":
    case "auth/invalid-credential":
    case "auth/user-not-found":
      return "Incorrect email or password.";
    case "auth/too-many-requests":
      return "Too many attempts. Please wait a moment and try again.";
    case "auth/invalid-api-key":
      return "Firebase API key is invalid. Verify your VITE_FIREBASE_* values.";
    case "auth/operation-not-allowed":
      return "Email/password auth is disabled in Firebase. Enable it in Authentication > Sign-in method.";
    case "auth/configuration-not-found":
      return "Firebase auth configuration is incomplete. Verify your web app settings.";
    case "auth/user-disabled":
      return "This account has been disabled.";
    case "auth/network-request-failed":
      return "Auth network request failed. Check Firebase web config, authorized domains, and browser network/adblock settings.";
    default:
      return "Authentication failed. Please try again.";
  }
}

async function onSubmit() {
  if (isSubmitting.value) return;
  errorMessage.value = "";

  if (isSignup.value && !name.value.trim()) {
    errorMessage.value = "Name is required.";
    return;
  }

  isSubmitting.value = true;
  try {
    if (isSignup.value) {
      await signupWithEmail(name.value, email.value, password.value);
      await router.push("/onboarding");
      return;
    }

    await loginWithEmail(email.value, password.value);
    await router.push("/dashboard");
  } catch (err) {
    errorMessage.value = mapAuthError(err);
  } finally {
    isSubmitting.value = false;
  }
}
</script>

<style scoped>
.auth-card {
  width: 100%;
  max-width: 520px;
  border-radius: 32px;
  overflow: hidden;
}

.auth-card__inner {
  padding: 40px;
}

.auth-card__label {
  margin: 0 0 20px;
  color: var(--accent);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: 0.2em;
  text-transform: uppercase;
}

.auth-card__title {
  margin: 0 0 16px;
  font-size: 36px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 0.95;
}

.auth-card__subtitle {
  margin: 0 0 24px;
  color: rgba(255, 255, 255, 0.6);
  font-size: 14px;
  line-height: 1.5;
}

.auth-card__group {
  margin-bottom: 20px;
}

.auth-card__field-label {
  margin: 0 0 16px;
  color: rgba(255, 255, 255, 0.62);
  font-size: 12px;
}

.auth-card__error {
  margin-bottom: 16px;
  border: 1px solid rgba(255, 106, 106, 0.55);
  background: rgba(255, 106, 106, 0.13);
  border-radius: 12px;
  padding: 10px 12px;
  color: #ffd0d0;
  font-size: 13px;
}

.auth-card__cta {
  width: 100%;
  margin-top: 12px;
}

.auth-card__footer {
  margin: 20px 0 0;
  text-align: center;
  color: rgba(255, 255, 255, 0.58);
  font-size: 12px;
}

.auth-card__footer a {
  color: var(--accent);
}

@media (max-width: 1023px) {
  .auth-card__inner {
    padding: 32px;
  }
}

@media (max-width: 767px) {
  .auth-card__inner {
    padding: 24px;
  }

  .auth-card__title {
    font-size: 32px;
  }
}
</style>
