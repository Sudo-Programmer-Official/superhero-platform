<template>
  <section class="public-deal">
    <div v-if="isLoading" class="state-card">Loading deal…</div>
    <div v-else-if="errorText" class="state-card state-card--error">{{ errorText }}</div>

    <template v-else-if="deal">
      <div v-if="checkoutNotice" class="state-card" :class="{ 'state-card--error': checkoutNoticeTone === 'error' }">
        {{ checkoutNotice }}
      </div>
      <article class="hero-card">
        <img v-if="deal.image" :src="deal.image" alt="Deal cover" class="hero-img" />
        <div v-else class="hero-img hero-img--fallback"></div>

        <div class="hero-body">
          <div class="hero-top">
            <div>
              <p class="badge">{{ deal.status.toUpperCase() }}</p>
              <h1>{{ deal.title }}</h1>
              <p class="sub">{{ deal.description || "A premium wellness experience." }}</p>
            </div>
            <p class="price">${{ deal.price }}</p>
          </div>

          <div class="meta-grid">
            <p><strong>Date</strong> {{ formatDate(deal.start_time) }}</p>
            <p><strong>Ends</strong> {{ formatDate(deal.end_time) }}</p>
            <p><strong>Location</strong> {{ deal.location }}</p>
            <p><strong>Availability</strong> {{ deal.remaining_slots }} / {{ deal.capacity }} left</p>
          </div>
        </div>
      </article>

      <div class="content-grid">
        <AppCard>
          <h2>About this deal</h2>
          <p class="copy">{{ deal.description || "This guided session is designed to help clients reset and restore." }}</p>

          <div class="host-card">
            <div class="host-avatar">OM</div>
            <div>
              <p class="host-name">Hosted by OpenMat Practitioner</p>
              <p class="host-meta">Trusted wellness partner · In-person redemption</p>
            </div>
          </div>
        </AppCard>

        <AppCard>
          <h2>Checkout</h2>
          <p class="copy">Select quantity, confirm attendee details, and continue to secure payment.</p>

          <div class="reserve-pill" :class="{ 'is-warning': reserveSeconds <= 120 }">
            Reservation held for {{ reserveTimeLabel }}
          </div>

          <div class="qty-row">
            <button class="qty-btn" type="button" :disabled="quantity <= 1" @click="quantity -= 1">−</button>
            <span class="qty-value">{{ quantity }}</span>
            <button class="qty-btn" type="button" :disabled="quantity >= maxQuantity" @click="quantity += 1">+</button>
          </div>

          <div class="checkout-fields">
            <label class="field">
              <span>Full name</span>
              <input
                v-model.trim="checkoutForm.name"
                type="text"
                autocomplete="name"
                placeholder="Alex Morgan"
                :disabled="checkoutState === 'processing'"
              />
            </label>
            <label class="field">
              <span>Email</span>
              <input
                v-model.trim="checkoutForm.email"
                type="email"
                autocomplete="email"
                placeholder="alex@example.com"
                :disabled="checkoutState === 'processing'"
              />
            </label>
            <label class="field field--full">
              <span>Phone (optional)</span>
              <input
                v-model.trim="checkoutForm.phone"
                type="tel"
                autocomplete="tel"
                placeholder="+1 312 555 0148"
                :disabled="checkoutState === 'processing'"
              />
            </label>
          </div>

          <p v-if="formError" class="form-error">{{ formError }}</p>

          <div class="summary">
            <div><span>Price</span><strong>${{ deal.price }}</strong></div>
            <div><span>Quantity</span><strong>{{ quantity }}</strong></div>
            <div><span>Subtotal</span><strong>${{ subtotal }}</strong></div>
            <div><span>Platform fee</span><strong>${{ fee }}</strong></div>
            <div><span>Estimated tax</span><strong>${{ tax }}</strong></div>
            <div class="total"><span>Total</span><strong>${{ total }}</strong></div>
          </div>

          <AppButton
            class="checkout-btn"
            variant="primary"
            size="form"
            :disabled="deal.status !== 'published' || checkoutState === 'processing'"
            @click="onCheckout"
          >
            {{ checkoutLabel }}
          </AppButton>

          <p class="checkout-note">Stripe-ready UI · secure checkout flow</p>
          <div class="status-row">
            <span class="status-chip" :class="`is-${checkoutState}`">{{ checkoutStateLabel }}</span>
            <span class="status-copy">{{ checkoutStatusCopy }}</span>
          </div>
        </AppCard>
      </div>

      <transition name="toast-fade">
        <div v-if="statusText" class="toast">{{ statusText }}</div>
      </transition>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute } from "vue-router";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import { createCheckoutSession, fetchPublicDeal, type DealCardPayload } from "../services/api";

type CheckoutState = "idle" | "processing" | "success" | "failed";

const route = useRoute();
const deal = ref<DealCardPayload | null>(null);
const statusText = ref("");
const errorText = ref("");
const isLoading = ref(true);
const checkoutState = ref<CheckoutState>("idle");
const quantity = ref(1);
const checkoutNotice = ref("");
const checkoutNoticeTone = ref<"ok" | "error">("ok");
const reserveSeconds = ref(9 * 60);
const formError = ref("");
const checkoutForm = ref({
  name: "",
  email: "",
  phone: ""
});
let reserveTimer: number | null = null;

const maxQuantity = computed(() => Math.max(1, Math.min(8, deal.value?.remaining_slots || 1)));
const unitPrice = computed(() => Number(deal.value?.price || 0));
const subtotal = computed(() => (unitPrice.value * quantity.value).toFixed(2));
const fee = computed(() => (Number(subtotal.value) * 0.05).toFixed(2));
const tax = computed(() => (Number(subtotal.value) * 0.08).toFixed(2));
const total = computed(() => (Number(subtotal.value) + Number(fee.value) + Number(tax.value)).toFixed(2));
const reserveTimeLabel = computed(() => {
  const minutes = Math.floor(reserveSeconds.value / 60)
    .toString()
    .padStart(2, "0");
  const seconds = Math.max(0, reserveSeconds.value % 60)
    .toString()
    .padStart(2, "0");
  return `${minutes}:${seconds}`;
});
const checkoutStateLabel = computed(() => {
  if (checkoutState.value === "processing") return "Processing";
  if (checkoutState.value === "success") return "Confirmed";
  if (checkoutState.value === "failed") return "Action needed";
  return "Ready";
});
const checkoutStatusCopy = computed(() => {
  if (checkoutState.value === "processing") return "Preparing secure payment session...";
  if (checkoutState.value === "success") return "Order accepted. Redirecting to payment.";
  if (checkoutState.value === "failed") return "Please review details and retry.";
  return "Secure checkout powered by Stripe.";
});

const checkoutLabel = computed(() => {
  if (checkoutState.value === "processing") return "Processing...";
  if (deal.value?.status !== "published") return "Unavailable";
  return `Pay $${total.value}`;
});

function formatDate(value: string): string {
  return new Date(value).toLocaleString();
}

function resetReservationTimer() {
  reserveSeconds.value = 9 * 60;
}

function startReservationTimer() {
  if (reserveTimer) window.clearInterval(reserveTimer);
  reserveTimer = window.setInterval(() => {
    if (checkoutState.value === "processing" || checkoutState.value === "success") {
      return;
    }
    if (reserveSeconds.value <= 0) {
      checkoutNotice.value = "Reservation expired. We refreshed your hold.";
      checkoutNoticeTone.value = "error";
      resetReservationTimer();
      quantity.value = 1;
      return;
    }
    reserveSeconds.value -= 1;
  }, 1000);
}

async function load() {
  const practitionerSlug = String(route.params.practitionerSlug || "");
  const dealSlug = String(route.params.dealSlug || "");
  if (!practitionerSlug || !dealSlug) {
    errorText.value = "Deal route is invalid.";
    isLoading.value = false;
    return;
  }

  try {
    deal.value = await fetchPublicDeal(practitionerSlug, dealSlug);
    quantity.value = 1;
    const checkoutQuery = String(route.query.checkout || "");
    if (checkoutQuery === "success") {
      checkoutNotice.value = "Payment completed successfully. Your pass will be issued shortly.";
      checkoutNoticeTone.value = "ok";
      checkoutState.value = "success";
    } else if (checkoutQuery === "cancel") {
      checkoutNotice.value = "Checkout was cancelled. You can retry any time.";
      checkoutNoticeTone.value = "error";
      checkoutState.value = "idle";
    } else if (checkoutQuery === "failed") {
      checkoutNotice.value = "Payment failed. Please retry checkout.";
      checkoutNoticeTone.value = "error";
      checkoutState.value = "failed";
    }
  } catch (err) {
    errorText.value = `Failed to load deal: ${String(err)}`;
  } finally {
    isLoading.value = false;
  }
}

async function onCheckout() {
  if (!deal.value) return;
  formError.value = "";
  if (!checkoutForm.value.name) {
    formError.value = "Enter your full name to continue.";
    checkoutState.value = "failed";
    return;
  }
  if (!checkoutForm.value.email || !checkoutForm.value.email.includes("@")) {
    formError.value = "Enter a valid email address to continue.";
    checkoutState.value = "failed";
    return;
  }
  if (reserveSeconds.value <= 0) {
    formError.value = "Reservation expired. Please retry checkout.";
    checkoutState.value = "failed";
    resetReservationTimer();
    return;
  }
  checkoutState.value = "processing";

  try {
    const res = await createCheckoutSession({
      deal_id: deal.value.id,
      customer_email: checkoutForm.value.email,
      customer_name: `${checkoutForm.value.name} x${quantity.value}`,
      success_url: `${window.location.origin}${window.location.pathname}?checkout=success`,
      cancel_url: `${window.location.origin}${window.location.pathname}?checkout=cancel`
    });

    checkoutState.value = "success";
    statusText.value = "Redirecting to payment...";
    window.location.href = res.checkout_url;
  } catch (err) {
    checkoutState.value = "failed";
    statusText.value = `Checkout failed: ${String(err)}`;
    checkoutNotice.value = "Checkout request failed. Please try again.";
    checkoutNoticeTone.value = "error";
  }
}

watch(quantity, () => {
  if (checkoutState.value !== "processing") {
    resetReservationTimer();
  }
});

onMounted(async () => {
  await load();
  startReservationTimer();
});

onBeforeUnmount(() => {
  if (reserveTimer) {
    window.clearInterval(reserveTimer);
    reserveTimer = null;
  }
});
</script>

<style scoped>
.public-deal { width: 100%; min-height: 100dvh; padding: 16px; display: grid; gap: 14px; }
.state-card { border-radius: 18px; border: 1px solid rgba(255,255,255,.12); background: rgba(13,21,36,.7); padding: 16px; color: #dbe5f3; }
.state-card--error { border-color: rgba(255,110,110,.6); color: #ffd0d0; }
.hero-card { overflow: hidden; border-radius: 24px; border: 1px solid rgba(255,255,255,.12); background: linear-gradient(180deg, rgba(8,14,27,.9), rgba(7,12,24,.85)); }
.hero-img { width: 100%; height: 280px; object-fit: cover; }
.hero-img--fallback { background: linear-gradient(145deg, rgba(33,54,89,.95), rgba(8,14,25,.92)); }
.hero-body { padding: 18px; }
.hero-top { display: flex; align-items: flex-start; justify-content: space-between; gap: 16px; }
.badge { margin: 0; font-size: 11px; letter-spacing: .12em; text-transform: uppercase; color: #f4d8a7; }
.hero-top h1 { margin: 8px 0 0; font-size: clamp(28px, 4vw, 44px); line-height: 1.05; }
.sub { margin: 10px 0 0; color: rgba(255,255,255,.72); }
.price { margin: 0; padding: 8px 12px; border-radius: 12px; border: 1px solid rgba(240,190,100,.4); background: rgba(240,190,100,.14); color: #f4d8a7; font-size: 28px; font-weight: 700; white-space: nowrap; }
.meta-grid { margin-top: 14px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px 14px; }
.meta-grid p { margin: 0; color: rgba(255,255,255,.78); font-size: 14px; }
.meta-grid strong { color: rgba(255,255,255,.98); margin-right: 6px; }
.content-grid { display: grid; grid-template-columns: 1fr 380px; gap: 14px; }
h2 { margin: 0 0 8px; font-size: 24px; }
.copy { margin: 0; color: rgba(255,255,255,.72); line-height: 1.6; }
.host-card { margin-top: 14px; border-radius: 14px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.03); padding: 12px; display: flex; align-items: center; gap: 10px; }
.host-avatar { width: 44px; height: 44px; border-radius: 999px; display: grid; place-items: center; background: linear-gradient(145deg, rgba(244,201,125,.3), rgba(77,57,31,.42)); border: 1px solid rgba(240,190,100,.34); color: #f4d8a7; font-weight: 700; }
.host-name { margin: 0; font-weight: 600; }
.host-meta { margin: 2px 0 0; color: rgba(255,255,255,.62); font-size: 13px; }
.qty-row { margin-top: 12px; display: flex; align-items: center; gap: 10px; }
.qty-btn { width: 38px; height: 38px; border-radius: 12px; border: 1px solid rgba(255,255,255,.14); background: rgba(255,255,255,.04); color: #dbe5f3; font-size: 20px; }
.qty-btn:disabled { opacity: .45; }
.qty-value { min-width: 34px; text-align: center; font-size: 20px; font-weight: 600; }
.reserve-pill { margin-top: 12px; border-radius: 999px; border: 1px solid rgba(113,182,255,.35); background: rgba(113,182,255,.12); color: #a7d5ff; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; padding: 8px 12px; width: fit-content; }
.reserve-pill.is-warning { border-color: rgba(255,170,120,.55); color: #f4d8a7; background: rgba(240,190,100,.14); }
.checkout-fields { margin-top: 12px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.field { display: grid; gap: 6px; }
.field span { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: rgba(255,255,255,.68); }
.field input { width: 100%; border-radius: 12px; border: 1px solid rgba(255,255,255,.14); background: rgba(11,17,28,.68); color: #e8eef8; padding: 10px 11px; }
.field--full { grid-column: span 2; }
.field input:focus { outline: none; border-color: rgba(240,190,100,.45); box-shadow: 0 0 0 2px rgba(240,190,100,.13); }
.form-error { margin: 10px 0 0; border-radius: 12px; border: 1px solid rgba(255,110,110,.55); background: rgba(120,22,22,.22); color: #ffd0d0; padding: 8px 10px; font-size: 13px; }
.summary { margin-top: 14px; display: grid; gap: 8px; }
.summary div { display: flex; align-items: center; justify-content: space-between; color: rgba(255,255,255,.74); }
.summary strong { color: #ecf2fb; }
.summary .total { margin-top: 4px; border-top: 1px solid rgba(255,255,255,.1); padding-top: 8px; color: #f4d8a7; }
.checkout-btn { margin-top: 14px; width: 100%; }
.checkout-note { margin: 10px 0 0; font-size: 12px; color: rgba(255,255,255,.55); }
.status-row { margin-top: 10px; display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.status-chip { border-radius: 999px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.04); color: rgba(255,255,255,.78); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; padding: 6px 10px; }
.status-chip.is-processing { border-color: rgba(113,182,255,.55); color: #9fd0ff; }
.status-chip.is-success { border-color: rgba(82,213,139,.58); color: #52d58b; }
.status-chip.is-failed { border-color: rgba(255,110,110,.55); color: #ffb2b2; }
.status-copy { color: rgba(255,255,255,.62); font-size: 12px; text-align: right; }
.toast { position: fixed; right: 18px; bottom: 18px; border-radius: 12px; border: 1px solid rgba(240,190,100,.32); background: rgba(10,16,29,.92); color: #f4d8a7; padding: 10px 12px; z-index: 40; }
.toast-fade-enter-active, .toast-fade-leave-active { transition: opacity 180ms ease, transform 180ms ease; }
.toast-fade-enter-from, .toast-fade-leave-to { opacity: 0; transform: translateY(8px); }
@media (max-width: 1120px) { .content-grid { grid-template-columns: 1fr; } }
@media (max-width: 767px) {
  .public-deal { padding: 10px; }
  .hero-img { height: 220px; }
  .hero-body { padding: 14px; }
  .hero-top { flex-direction: column; }
  .price { font-size: 24px; }
  .meta-grid { grid-template-columns: 1fr; }
  .checkout-fields { grid-template-columns: 1fr; }
  .field--full { grid-column: span 1; }
  .status-row { flex-direction: column; align-items: flex-start; }
  .status-copy { text-align: left; }
}
</style>
