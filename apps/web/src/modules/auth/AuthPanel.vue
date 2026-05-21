<template>
  <article class="deal-card">
    <p class="deal-title">Sign in</p>
    <div class="auth-grid">
      <button class="ghost-btn" @click="onGoogle">Continue with Google</button>
      <input v-model="email" placeholder="Email" class="field" />
      <input v-model="password" placeholder="Password" type="password" class="field" />
      <button class="ghost-btn" @click="onEmail">Continue with Email</button>
    </div>
  </article>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { loginWithEmail, loginWithGoogle } from "../../firebase/auth";
import { sessionState } from "../../stores/session";

const email = ref("");
const password = ref("");

async function onGoogle() {
  try {
    await loginWithGoogle();
    sessionState.statusText = "Google sign-in success";
  } catch (err) {
    sessionState.statusText = `Google sign-in failed: ${String(err)}`;
  }
}

async function onEmail() {
  try {
    await loginWithEmail(email.value, password.value);
    sessionState.statusText = "Email sign-in success";
  } catch (err) {
    sessionState.statusText = `Email sign-in failed: ${String(err)}`;
  }
}
</script>
