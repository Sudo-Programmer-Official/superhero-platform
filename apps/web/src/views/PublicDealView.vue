<template>
  <section class="public-deal">
    <template v-if="isLoading">
      <article class="hero-card skeleton">
        <div class="hero-img hero-img--fallback shimmer"></div>
        <div class="hero-body">
          <div class="skeleton-line w-24"></div>
          <div class="skeleton-line w-80"></div>
          <div class="skeleton-line w-56"></div>
        </div>
      </article>
      <div class="content-grid">
        <AppCard class="skeleton">
          <div class="skeleton-line w-40"></div>
          <div class="skeleton-line w-full"></div>
          <div class="skeleton-line w-92"></div>
        </AppCard>
        <AppCard class="skeleton">
          <div class="skeleton-line w-48"></div>
          <div class="skeleton-line w-64"></div>
          <div class="skeleton-line w-full"></div>
        </AppCard>
      </div>
    </template>
    <div v-else-if="errorText" class="state-card state-card--error">{{ errorText }}</div>

    <template v-else-if="deal">
      <div v-if="checkoutNotice" class="state-card" :class="{ 'state-card--error': checkoutNoticeTone === 'error' }">
        {{ checkoutNotice }}
      </div>

      <article class="hero-card">
        <img v-if="deal.image" :src="deal.image" alt="Deal cover" class="hero-img" loading="eager" fetchpriority="high" />
        <div v-else class="hero-img hero-img--fallback"></div>
        <div class="hero-overlay"></div>

        <div class="hero-body">
          <div class="hero-top">
            <div>
              <p class="badge">{{ getStatusLabel(deal.status) }}</p>
              <h1>{{ deal.title }}</h1>
              <p class="sub">{{ deal.description || "A premium wellness experience." }}</p>
            </div>
            <div class="price-block">
              <p class="price">{{ formatMoney(deal.base_price, deal.currency) }}</p>
              <p class="price-caption">per attendee</p>
            </div>
          </div>

          <div class="meta-grid">
            <p><strong>Date</strong> {{ formatDate(deal.start_time) }}</p>
            <p><strong>Ends</strong> {{ formatDate(deal.end_time) }}</p>
            <p><strong>Location</strong> {{ deal.location || "TBD" }}</p>
            <p><strong>Availability</strong> {{ deal.remaining_slots }} / {{ deal.capacity }} left</p>
          </div>
        </div>
      </article>

      <div class="content-grid">
        <div class="content-stack">
          <AppCard>
            <h2>About this experience</h2>
            <p class="copy">{{ deal.description || "This guided session is designed to help clients reset and restore." }}</p>

            <div class="trust-row">
              <span>Secure booking</span>
              <span>Instant confirmation</span>
              <span>QR access included</span>
              <span>Refund protected</span>
            </div>
          </AppCard>

          <AppCard>
            <h3>Hosted by</h3>
            <div class="host-card">
              <div class="host-avatar">OM</div>
              <div class="host-main">
                <p class="host-name">OpenMat Practitioner</p>
                <p class="host-meta">Wellness · Verified host</p>
              </div>
              <div class="host-stats">143+ hosted</div>
            </div>
            <div class="proof-row">
              <span>4.9 host rating</span>
              <span>12 people viewed today</span>
              <span>Repeat attendees welcome</span>
            </div>
          </AppCard>
        </div>

        <AppCard class="checkout-card desktop-checkout">
          <h2>Reserve your spot</h2>
          <p class="copy">Complete details to secure your booking.</p>
          <CheckoutPanelContent />
        </AppCard>
      </div>

      <div class="mobile-cta" v-if="isMobileViewport">
        <div>
          <p class="mobile-cta-price">{{ total }}</p>
          <p class="mobile-cta-sub">{{ quantity }} attendee · includes fees</p>
        </div>
        <button
          class="mobile-cta-btn"
          type="button"
          :disabled="deal.status !== 'published' || checkoutState === 'processing'"
          @click="mobileSheetOpen = true"
        >
          {{ checkoutState === "processing" ? "Reserving your spot..." : "Reserve Spot" }}
        </button>
      </div>

      <div v-if="mobileSheetOpen" class="sheet-backdrop" @click.self="mobileSheetOpen = false">
        <section class="mobile-sheet" role="dialog" aria-modal="true" aria-label="Checkout">
          <div class="sheet-handle"></div>
          <div class="sheet-head">
            <h2>Checkout</h2>
            <button class="sheet-close" type="button" @click="mobileSheetOpen = false">Close</button>
          </div>
          <CheckoutPanelContent />
        </section>
      </div>

      <AppCard v-if="isSuccessState" class="success-card">
        <h2>Booking confirmed</h2>
        <p class="copy">Your reservation is secured and confirmation is on its way.</p>
        <div class="success-grid">
          <p v-if="checkoutBookingNumber">Booking #{{ checkoutBookingNumber }}</p>
          <p>Confirmation email sent</p>
          <p>Wallet pass generated</p>
          <p>QR code ready for entry</p>
        </div>
        <div class="success-actions">
          <button type="button" class="success-btn" @click="openPass">View Pass</button>
          <button type="button" class="success-btn" @click="downloadQr">Download QR</button>
          <button type="button" class="success-btn is-secondary" @click="goHome">Return Home</button>
        </div>
      </AppCard>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import { calculateCheckoutTotals, formatLocalDateTime, formatMoney, formatTimezone, getStatusLabel } from "../domain/deal";
import { createCheckoutSession, fetchCheckoutResult, fetchPublicDeal, type DealCardPayload } from "../services/api";
import { showToast } from "../stores/toast";

type CheckoutState = "idle" | "processing" | "success" | "failed";

const route = useRoute();
const router = useRouter();
const deal = ref<DealCardPayload | null>(null);
const errorText = ref("");
const isLoading = ref(true);
const checkoutState = ref<CheckoutState>("idle");
const quantity = ref(1);
const checkoutNotice = ref("");
const checkoutNoticeTone = ref<"ok" | "error">("ok");
const reserveSeconds = ref(9 * 60);
const formError = ref("");
const mobileSheetOpen = ref(false);
const viewportWidth = ref(typeof window !== "undefined" ? window.innerWidth : 1280);
const checkoutSessionId = ref("");
const walletPassUrl = ref<string | null>(null);
const checkoutQrCode = ref<string | null>(null);
const checkoutBookingNumber = ref<string | null>(null);
const checkoutForm = ref({
  name: "",
  email: "",
  phone: ""
});
let reserveTimer: number | null = null;

const isMobileViewport = computed(() => viewportWidth.value <= 767);
const isSuccessState = computed(() => checkoutState.value === "success" && String(route.query.checkout || "") === "success");
const maxQuantity = computed(() => Math.max(1, Math.min(8, deal.value?.remaining_slots || 1)));
const checkoutTotals = computed(() => {
  if (!deal.value) return null;
  return calculateCheckoutTotals(deal.value, quantity.value);
});
const subtotal = computed(() => checkoutTotals.value?.formatted.subtotal ?? formatMoney(0));
const fee = computed(() => checkoutTotals.value?.formatted.fee ?? formatMoney(0));
const tax = computed(() => checkoutTotals.value?.formatted.tax ?? formatMoney(0));
const total = computed(() => checkoutTotals.value?.formatted.total ?? formatMoney(0));
const lowStock = computed(() => (deal.value?.remaining_slots ?? 0) > 0 && (deal.value?.remaining_slots ?? 0) <= 4);
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
  if (checkoutState.value === "processing") return "Reserving";
  if (checkoutState.value === "success") return "Confirmed";
  if (checkoutState.value === "failed") return "Needs action";
  return "Ready";
});
const checkoutStatusCopy = computed(() => {
  if (checkoutState.value === "processing") return "Creating secure payment session...";
  if (checkoutState.value === "success") return "Reservation accepted. Redirecting to payment.";
  if (checkoutState.value === "failed") return "Please review details and retry.";
  return "Secure checkout powered by Stripe.";
});

const checkoutLabel = computed(() => {
  if (checkoutState.value === "processing") return "Reserving your spot...";
  if (deal.value?.status !== "published") return "Unavailable";
  return `Reserve for ${total.value}`;
});

function formatDate(value: string): string {
  const tz = deal.value?.timezone || "UTC";
  return `${formatLocalDateTime(value, tz)} ${formatTimezone(value, tz)}`;
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

function onViewportResize() {
  viewportWidth.value = window.innerWidth;
  if (viewportWidth.value > 767) {
    mobileSheetOpen.value = false;
  }
}

async function syncCheckoutArtifacts(sessionId: string) {
  let attempts = 0;
  while (attempts < 8) {
    attempts += 1;
    const result = await fetchCheckoutResult(sessionId);
    if (result.status === "ready") {
      walletPassUrl.value = result.pass_url;
      checkoutQrCode.value = result.qr_code;
      checkoutBookingNumber.value = result.booking_number;
      return;
    }
    await new Promise((resolve) => window.setTimeout(resolve, 1500));
  }
}

function openPass() {
  if (walletPassUrl.value) {
    window.open(walletPassUrl.value, "_blank", "noopener,noreferrer");
    return;
  }
  showToast("Pass link will appear as soon as issuance completes.", "loading", 2200);
}

function downloadQr() {
  if (checkoutQrCode.value) {
    const blob = new Blob([checkoutQrCode.value], { type: "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `openmat-qr-${checkoutBookingNumber.value || "booking"}.txt`;
    document.body.appendChild(link);
    link.click();
    link.remove();
    URL.revokeObjectURL(url);
    return;
  }
  showToast("QR is being prepared. Check your email shortly.", "loading", 2200);
}

function goHome() {
  router.push(`/openmat/${String(route.params.practitionerSlug || "")}`);
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
      checkoutSessionId.value = String(route.query.session_id || "");
      if (checkoutSessionId.value) {
        try {
          await syncCheckoutArtifacts(checkoutSessionId.value);
        } catch {
          // Do not fail page load if pass issuance is still propagating.
        }
      }
      const handoffPayload = {
        at: new Date().toISOString(),
        dealId: deal.value.id,
        dealSlug,
        email: checkoutForm.value.email || null,
        session_id: checkoutSessionId.value || null
      };
      window.localStorage.setItem("openmat:last-checkout-success", JSON.stringify(handoffPayload));
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
      quantity: quantity.value,
      success_url: `${window.location.origin}${window.location.pathname}?checkout=success`,
      cancel_url: `${window.location.origin}${window.location.pathname}?checkout=cancel`
    });

    checkoutState.value = "success";
    showToast("Redirecting to payment...", "loading", 1800);
    window.location.href = res.checkout_url;
  } catch (err) {
    checkoutState.value = "failed";
    showToast(`Checkout failed: ${String(err)}`, "error");
    checkoutNotice.value = "Checkout request failed. Please try again.";
    checkoutNoticeTone.value = "error";
  }
}

const CheckoutPanelContent = defineComponent({
  name: "CheckoutPanelContent",
  setup() {
    return () =>
      h("div", { class: ["checkout-shell", isMobileViewport.value ? "is-mobile" : ""] }, [
        h("div", { class: "checkout-price" }, [
          h("p", { class: "checkout-price-value" }, formatMoney(deal.value?.base_price, deal.value?.currency)),
          h("p", { class: "checkout-price-sub" }, "per attendee")
        ]),
        h("div", { class: "scarcity-row" }, [
          h("span", { class: ["scarcity-pill", lowStock.value ? "is-hot" : ""] }, lowStock.value ? `Only ${deal.value?.remaining_slots} spots left` : "Spots available"),
          h("span", { class: "scarcity-pill" }, "High demand this week")
        ]),
        h("div", { class: ["reserve-pill", reserveSeconds.value <= 120 ? "is-warning" : ""] }, `Reservation held for ${reserveTimeLabel.value}`),
        h("div", { class: "qty-row" }, [
          h("button", { class: "qty-btn", type: "button", disabled: quantity.value <= 1, onClick: () => (quantity.value -= 1) }, "−"),
          h("span", { class: "qty-value" }, String(quantity.value)),
          h("button", { class: "qty-btn", type: "button", disabled: quantity.value >= maxQuantity.value, onClick: () => (quantity.value += 1) }, "+")
        ]),
        h("div", { class: "checkout-fields" }, [
          h("label", { class: "field" }, [
            h("span", "Full name"),
            h("input", {
              value: checkoutForm.value.name,
              onInput: (event: Event) => {
                checkoutForm.value.name = (event.target as HTMLInputElement).value;
              },
              type: "text",
              autocomplete: "name",
              placeholder: "Alex Morgan",
              disabled: checkoutState.value === "processing"
            })
          ]),
          h("label", { class: "field" }, [
            h("span", "Email"),
            h("input", {
              value: checkoutForm.value.email,
              onInput: (event: Event) => {
                checkoutForm.value.email = (event.target as HTMLInputElement).value;
              },
              type: "email",
              autocomplete: "email",
              placeholder: "alex@example.com",
              disabled: checkoutState.value === "processing"
            })
          ]),
          h("label", { class: "field field--full" }, [
            h("span", "Phone (optional)"),
            h("input", {
              value: checkoutForm.value.phone,
              onInput: (event: Event) => {
                checkoutForm.value.phone = (event.target as HTMLInputElement).value;
              },
              type: "tel",
              autocomplete: "tel",
              placeholder: "+1 312 555 0148",
              disabled: checkoutState.value === "processing"
            })
          ])
        ]),
        formError.value ? h("p", { class: "form-error" }, formError.value) : null,
        h("div", { class: "summary-wrap" }, [
          h("div", { class: "summary" }, [
            h("div", [h("span", "Price"), h("strong", formatMoney(deal.value?.base_price, deal.value?.currency))]),
            h("div", [h("span", "Quantity"), h("strong", String(quantity.value))]),
            h("div", [h("span", "Subtotal"), h("strong", subtotal.value)]),
            h("div", [h("span", "Platform fee"), h("strong", fee.value)]),
            h("div", [h("span", "Estimated tax"), h("strong", tax.value)]),
            h("div", { class: "total" }, [h("span", "Total"), h("strong", total.value)])
          ])
        ]),
        h("div", { class: "action-wrap" }, [
          h(
            AppButton,
            {
              class: "checkout-btn",
              variant: "primary",
              size: "form",
              disabled: deal.value?.status !== "published" || checkoutState.value === "processing",
              onClick: onCheckout
            },
            { default: () => checkoutLabel.value }
          ),
          h("div", { class: "status-row" }, [
            h("span", { class: ["status-chip", `is-${checkoutState.value}`] }, checkoutStateLabel.value),
            h("span", { class: "status-copy" }, checkoutStatusCopy.value)
          ])
        ])
      ]);
  }
});

watch(quantity, () => {
  if (checkoutState.value !== "processing") {
    resetReservationTimer();
  }
});

onMounted(async () => {
  await load();
  startReservationTimer();
  window.addEventListener("resize", onViewportResize, { passive: true });
});

onBeforeUnmount(() => {
  if (reserveTimer) {
    window.clearInterval(reserveTimer);
    reserveTimer = null;
  }
  window.removeEventListener("resize", onViewportResize);
});
</script>

<style scoped>
.public-deal {
  --bg-0: #030b18;
  --bg-1: #081a32;
  --line: rgba(255, 255, 255, 0.14);
  --text-muted: rgba(230, 238, 249, 0.72);
  width: 100%;
  min-height: 100dvh;
  padding: 0;
  display: grid;
  gap: 18px;
  background: radial-gradient(900px 420px at 15% -10%, rgba(38, 91, 169, 0.18), transparent 60%), linear-gradient(180deg, var(--bg-1), var(--bg-0));
}
.public-deal > * {
  width: min(100%, 1440px);
  margin-inline: auto;
  padding-inline: clamp(16px, 2.1vw, 32px);
}
.hero-card,
.content-stack > :deep(*),
.checkout-card,
.success-card {
  animation: riseIn 420ms ease-out both;
}
@keyframes riseIn {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}
.state-card { border-radius: 18px; border: 1px solid var(--line); background: rgba(13,21,36,.7); padding: 16px; color: #dbe5f3; }
.state-card--error { border-color: rgba(255,110,110,.6); color: #ffd0d0; }
.hero-card { position: relative; overflow: hidden; border-radius: 26px; border: 1px solid var(--line); background: #050e1e; }
.hero-img { width: 100%; height: clamp(340px, 36vw, 420px); object-fit: cover; object-position: center; display: block; }
.hero-img--fallback { background: linear-gradient(145deg, rgba(33,54,89,.95), rgba(8,14,25,.92)); }
.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(180deg, rgba(0,0,0,0.12) 0%, rgba(2,6,23,0.82) 72%, rgba(2,6,23,0.98) 100%);
}
.hero-body { position: absolute; inset: auto 0 0; padding: 24px; z-index: 2; }
.hero-top { display: flex; align-items: flex-end; justify-content: space-between; gap: 16px; }
.badge { margin: 0; font-size: 11px; letter-spacing: .16em; text-transform: uppercase; color: #f5dca4; }
.hero-top h1 { margin: 8px 0 0; font-size: clamp(36px, 4.6vw, 60px); line-height: 0.98; letter-spacing: -0.03em; }
.sub { margin: 10px 0 0; color: var(--text-muted); max-width: 62ch; }
.price-block { display: grid; justify-items: end; gap: 4px; }
.price { margin: 0; padding: 10px 14px; border-radius: 14px; border: 1px solid rgba(240,190,100,.45); background: rgba(240,190,100,.14); color: #f4d8a7; font-size: 34px; font-weight: 700; white-space: nowrap; }
.price-caption { margin: 0; font-size: 12px; color: rgba(255,255,255,.78); text-transform: uppercase; letter-spacing: .08em; }
.meta-grid { margin-top: 18px; display: grid; grid-template-columns: 1fr 1fr; gap: 10px 16px; }
.meta-grid p { margin: 0; color: rgba(255,255,255,.8); font-size: 14px; }
.meta-grid strong { color: rgba(255,255,255,.96); margin-right: 6px; }
.content-grid { display: grid; grid-template-columns: minmax(0,1fr) clamp(380px, 30vw, 420px); gap: 20px; align-items: start; }
.content-stack { display: grid; gap: 18px; min-width: 0; }
h2 { margin: 0 0 8px; font-size: 34px; line-height: 1.05; letter-spacing: -0.02em; }
h3 { margin: 0 0 8px; font-size: 20px; }
.copy { margin: 0; color: var(--text-muted); line-height: 1.65; }
.trust-row { margin-top: 14px; display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.trust-row span { border: 1px solid rgba(82,213,139,.28); background: rgba(82,213,139,.08); color: #d2f9e3; border-radius: 999px; padding: 8px 12px; font-size: 12px; }
.host-card { border-radius: 16px; border: 1px solid var(--line); background: rgba(255,255,255,.04); padding: 14px; display: flex; align-items: center; gap: 12px; }
.host-avatar { width: 54px; height: 54px; border-radius: 999px; display: grid; place-items: center; background: linear-gradient(145deg, rgba(244,201,125,.34), rgba(77,57,31,.44)); border: 1px solid rgba(240,190,100,.34); color: #f4d8a7; font-weight: 700; }
.host-main { flex: 1; }
.host-name { margin: 0; font-size: 18px; font-weight: 650; }
.host-meta { margin: 3px 0 0; color: rgba(255,255,255,.65); font-size: 13px; }
.host-stats { border: 1px solid rgba(113,182,255,.38); background: rgba(113,182,255,.12); color: #afdaff; border-radius: 999px; padding: 8px 10px; font-size: 12px; }
.proof-row { margin-top: 10px; display: flex; gap: 10px; flex-wrap: wrap; }
.proof-row span { font-size: 12px; color: rgba(255,255,255,.74); border: 1px solid var(--line); border-radius: 999px; padding: 6px 10px; }
.checkout-card { position: sticky; top: 24px; width: 100%; min-width: 380px; max-width: 420px; justify-self: end; flex-shrink: 0; }
.checkout-shell { display: grid; gap: 16px; min-width: 0; }
.checkout-price { display: flex; justify-content: space-between; align-items: baseline; }
.checkout-price-value { margin: 0; font-size: 36px; font-weight: 700; color: #f6dfb2; }
.checkout-price-sub { margin: 0; color: rgba(255,255,255,.68); text-transform: uppercase; letter-spacing: .08em; font-size: 11px; }
.scarcity-row { display: flex; gap: 8px; flex-wrap: wrap; }
.scarcity-pill { border-radius: 999px; border: 1px solid rgba(255,255,255,.2); padding: 7px 10px; font-size: 12px; color: rgba(255,255,255,.8); }
.scarcity-pill.is-hot { border-color: rgba(255,170,120,.55); color: #ffd8b2; background: rgba(240,190,100,.14); }
.qty-row { display: flex; align-items: center; gap: 10px; }
.qty-btn { width: 42px; height: 42px; border-radius: 12px; border: 1px solid var(--line); background: rgba(255,255,255,.04); color: #dbe5f3; font-size: 21px; transition: transform 160ms ease; }
.qty-btn:hover:not(:disabled) { transform: translateY(-1px); }
.qty-btn:disabled { opacity: .45; }
.qty-value { min-width: 34px; text-align: center; font-size: 22px; font-weight: 600; }
.reserve-pill { border-radius: 999px; border: 1px solid rgba(113,182,255,.35); background: rgba(113,182,255,.12); color: #a7d5ff; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; padding: 8px 12px; width: fit-content; }
.reserve-pill.is-warning { border-color: rgba(255,170,120,.55); color: #f4d8a7; background: rgba(240,190,100,.14); box-shadow: 0 0 22px rgba(240,190,100,.24); animation: timerPulse 1.8s ease-in-out infinite; }
@keyframes timerPulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.015); } }
.checkout-fields { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(280px, 100%), 1fr)); gap: 14px; min-width: 0; }
.field { display: grid; gap: 6px; }
.field span { font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: rgba(255,255,255,.68); }
.field input { width: 100%; min-width: 0; border-radius: 13px; border: 1px solid var(--line); background: rgba(11,17,28,.7); color: #e8eef8; padding: 13px 12px; min-height: 48px; }
.field--full { grid-column: span 2; }
.field input:focus { outline: none; border-color: rgba(240,190,100,.45); box-shadow: 0 0 0 2px rgba(240,190,100,.13); }
.form-error { margin: 0; border-radius: 12px; border: 1px solid rgba(255,110,110,.55); background: rgba(120,22,22,.22); color: #ffd0d0; padding: 8px 10px; font-size: 13px; }
.summary-wrap { border-top: 1px solid rgba(255,255,255,.08); padding-top: 12px; }
.summary { display: grid; gap: 8px; }
.summary div { display: flex; align-items: center; justify-content: space-between; color: rgba(255,255,255,.74); }
.summary strong { color: #ecf2fb; }
.summary .total { margin-top: 6px; border-top: 1px solid var(--line); padding-top: 10px; color: #f4d8a7; font-size: 18px; }
.action-wrap { display: grid; gap: 12px; }
.checkout-btn { width: 100%; min-height: 52px; }
.checkout-btn:hover { filter: brightness(1.06); }
.status-row { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.status-chip { border-radius: 999px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.04); color: rgba(255,255,255,.78); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; padding: 6px 10px; }
.status-chip.is-processing { border-color: rgba(113,182,255,.55); color: #9fd0ff; }
.status-chip.is-success { border-color: rgba(82,213,139,.58); color: #52d58b; }
.status-chip.is-failed { border-color: rgba(255,110,110,.55); color: #ffb2b2; }
.status-copy { color: rgba(255,255,255,.62); font-size: 12px; text-align: right; }
.success-card { border: 1px solid rgba(82,213,139,.36); background: linear-gradient(145deg, rgba(82,213,139,.09), rgba(16,34,26,.9)); }
.success-grid { margin-top: 10px; display: grid; gap: 8px; }
.success-grid p { margin: 0; color: rgba(223, 255, 236, 0.92); }
.success-actions { margin-top: 12px; display: flex; gap: 10px; flex-wrap: wrap; }
.success-btn {
  border: 1px solid rgba(82,213,139,.5);
  background: rgba(82,213,139,.14);
  color: #d9ffe9;
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 600;
  transition: transform 160ms ease, background 160ms ease;
}
.success-btn:hover { transform: translateY(-1px); background: rgba(82,213,139,.2); }
.success-btn.is-secondary {
  border-color: var(--line);
  background: rgba(255,255,255,.05);
  color: #e8eef8;
}
.mobile-cta { display: none; }
.sheet-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(2, 6, 16, 0.56);
  backdrop-filter: blur(8px);
  z-index: 48;
  display: grid;
  align-items: end;
}
.mobile-sheet {
  border-radius: 24px 24px 0 0;
  border: 1px solid var(--line);
  border-bottom: none;
  background: linear-gradient(180deg, rgba(9, 20, 38, 0.98), rgba(5, 12, 24, 0.99));
  max-height: 90dvh;
  overflow: hidden;
  display: grid;
  grid-template-rows: auto 1fr;
  padding: 14px 14px calc(12px + env(safe-area-inset-bottom, 0px));
}
.sheet-handle { width: 56px; height: 5px; border-radius: 999px; background: rgba(255,255,255,.24); margin: 0 auto 10px; }
.sheet-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.sheet-close { border: 1px solid var(--line); background: rgba(255,255,255,.05); color: #dfe8f8; border-radius: 10px; padding: 8px 10px; }
.mobile-sheet .checkout-shell { overflow-y: auto; padding-bottom: calc(120px + env(safe-area-inset-bottom, 0px)); }
.mobile-sheet .summary-wrap {
  position: sticky;
  bottom: calc(88px + env(safe-area-inset-bottom, 0px));
  background: linear-gradient(180deg, rgba(9,20,38,0.2), rgba(9,20,38,0.95) 36%);
  padding-top: 14px;
}
.mobile-sheet .action-wrap {
  position: sticky;
  bottom: 0;
  background: linear-gradient(180deg, rgba(9,20,38,0.18), rgba(9,20,38,0.98) 34%);
  padding-top: 10px;
  padding-bottom: calc(6px + env(safe-area-inset-bottom, 0px));
}
.skeleton { opacity: 0.92; }
.skeleton-line {
  height: 12px;
  border-radius: 999px;
  background: linear-gradient(90deg, rgba(255,255,255,.1), rgba(255,255,255,.18), rgba(255,255,255,.1));
  background-size: 200% 100%;
  animation: shimmer 1.2s linear infinite;
  margin-bottom: 10px;
}
.w-24 { width: 24%; }
.w-40 { width: 40%; }
.w-48 { width: 48%; }
.w-56 { width: 56%; }
.w-64 { width: 64%; }
.w-80 { width: 80%; }
.w-92 { width: 92%; }
.w-full { width: 100%; }
.shimmer { animation: shimmer 1.4s linear infinite; }
@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

@media (max-width: 1360px) {
  .content-grid { grid-template-columns: minmax(0,1fr) clamp(360px, 33vw, 400px); }
  .checkout-card { min-width: 360px; max-width: 400px; }
}
@media (max-width: 1120px) {
  .content-grid { grid-template-columns: 1fr; }
  .desktop-checkout { position: static; max-width: none; min-width: 0; justify-self: stretch; }
}
@media (max-width: 1024px) {
  .hero-img { height: clamp(260px, 34vw, 320px); }
  .public-deal > * { padding-inline: 20px; }
}
@media (max-width: 767px) {
  .public-deal { padding-bottom: calc(94px + env(safe-area-inset-bottom, 0px)); }
  .public-deal > * { padding-inline: 16px; }
  .hero-img { height: clamp(220px, 54vw, 260px); }
  .hero-body { position: relative; inset: auto; padding: 14px; }
  .hero-overlay { background: linear-gradient(180deg, rgba(0,0,0,0.06) 0%, rgba(2,6,23,0.62) 76%, rgba(2,6,23,0.95) 100%); }
  .hero-top { flex-direction: column; align-items: flex-start; }
  .price-block { justify-items: start; }
  .price { font-size: 28px; }
  .meta-grid { grid-template-columns: 1fr; }
  .trust-row { grid-template-columns: 1fr; }
  .desktop-checkout { display: none; }
  .mobile-cta {
    display: flex;
    position: fixed;
    left: 10px;
    right: 10px;
    bottom: calc(10px + env(safe-area-inset-bottom, 0px));
    z-index: 40;
    align-items: center;
    justify-content: space-between;
    gap: 10px;
    border: 1px solid var(--line);
    background: rgba(6, 15, 30, 0.95);
    backdrop-filter: blur(8px);
    border-radius: 16px;
    padding: 10px;
  }
  .mobile-cta-price { margin: 0; font-size: 22px; color: #f6dfb2; font-weight: 700; }
  .mobile-cta-sub { margin: 2px 0 0; font-size: 12px; color: rgba(255,255,255,.65); }
  .mobile-cta-btn {
    border: 1px solid rgba(240,190,100,.46);
    color: #051227;
    background: linear-gradient(145deg, #f3d89f, #e9c57b);
    border-radius: 12px;
    padding: 11px 14px;
    font-weight: 700;
    white-space: nowrap;
  }
  .checkout-fields { grid-template-columns: 1fr; gap: 14px; }
  .field--full { grid-column: span 1; }
  .status-row { flex-direction: column; align-items: flex-start; }
  .status-copy { text-align: left; }
}
</style>
