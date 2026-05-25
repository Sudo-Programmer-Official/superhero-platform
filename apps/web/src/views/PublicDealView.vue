<template>
  <section class="public-deal">
    <div class="page-shell">
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
            <div class="card-inner">
              <h2>About this experience</h2>
              <p class="copy">{{ deal.description || "This guided session is designed to help clients reset and restore." }}</p>

              <div class="trust-row">
                <span>Secure booking</span>
                <span>Instant confirmation</span>
                <span>QR access included</span>
                <span>Refund protected</span>
              </div>
            </div>
          </AppCard>

          <AppCard>
            <div class="card-inner">
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
            </div>
          </AppCard>
        </div>

        <AppCard class="checkout-card desktop-checkout">
          <div class="card-inner card-inner--checkout">
            <h2>Reserve your spot</h2>
            <p class="copy">Complete details to secure your booking.</p>
            <CheckoutPanelContent />
          </div>
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
          :disabled="deal.status !== 'published' || isCheckoutBusy"
          @click="mobileSheetOpen = true"
        >
          {{ isCheckoutBusy ? "Reserving your spot..." : "Reserve Spot" }}
        </button>
      </div>

      <div v-if="mobileSheetOpen" class="sheet-backdrop" @click.self="!isCheckoutBusy && (mobileSheetOpen = false)">
        <section class="mobile-sheet" role="dialog" aria-modal="true" aria-label="Checkout">
          <div class="sheet-handle"></div>
          <div class="sheet-head">
            <h2>Checkout</h2>
            <button class="sheet-close" type="button" :disabled="isCheckoutBusy" @click="mobileSheetOpen = false">Close</button>
          </div>
          <div class="sheet-content">
            <CheckoutPanelContent />
          </div>
        </section>
      </div>

    </template>
    </div>

  </section>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import { calculateCheckoutTotals, formatLocalDateTime, formatMoney, formatTimezone, getStatusLabel } from "../domain/deal";
import { createCheckoutSession, fetchPublicDeal, type DealCardPayload } from "../services/api";
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
const checkoutForm = ref({
  name: "",
  email: "",
  phone: ""
});
let reserveTimer: number | null = null;

const isMobileViewport = computed(() => viewportWidth.value <= 767);
const isCheckoutBusy = computed(() => checkoutState.value === "processing");
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

async function load() {
  const practitionerSlug = String(route.params.practitionerSlug || "");
  const dealSlug = String(route.params.dealSlug || "");
  if (!practitionerSlug || !dealSlug) {
    errorText.value = "Deal route is invalid.";
    isLoading.value = false;
    return;
  }

  try {
    if (String(route.query.checkout || "") === "success") {
      await router.replace({
        name: "public-deal-success",
        params: { practitionerSlug, dealSlug },
        query: route.query
      });
      return;
    }
    deal.value = await fetchPublicDeal(practitionerSlug, dealSlug);
    quantity.value = 1;
    const checkoutQuery = String(route.query.checkout || "");
    if (checkoutQuery === "cancel") {
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
      success_url: `${window.location.origin}/openmat/${String(route.params.practitionerSlug || "")}/${String(route.params.dealSlug || "")}/booking-confirmed?checkout=success`,
      cancel_url: `${window.location.origin}${window.location.pathname}?checkout=cancel`
    });

    checkoutState.value = "success";
    window.localStorage.setItem(
      "openmat:last-checkout-success",
      JSON.stringify({
        at: new Date().toISOString(),
        dealId: deal.value.id,
        dealSlug: String(route.params.dealSlug || ""),
        email: checkoutForm.value.email || null,
        name: checkoutForm.value.name || null
      })
    );
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

watch(mobileSheetOpen, (open) => {
  if (typeof document === "undefined") return;
  document.body.style.overflow = open ? "hidden" : "";
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
  if (typeof document !== "undefined") {
    document.body.style.overflow = "";
  }
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
.page-shell {
  width: min(100%, 1440px);
  margin-inline: auto;
  padding-inline: 32px;
  padding-block: 18px;
  display: grid;
  gap: 18px;
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
.content-grid { display: grid; grid-template-columns: minmax(0,1fr) minmax(400px, 440px); gap: 22px; align-items: start; }
.content-stack { display: grid; gap: 18px; min-width: 0; }
.card-inner {
  padding: 24px;
  display: grid;
  gap: 14px;
}
.card-inner--checkout {
  gap: 16px;
}
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
.checkout-card { position: sticky; top: 24px; width: 100%; min-width: 400px; max-width: 440px; justify-self: end; flex-shrink: 0; }
.public-deal :deep(.checkout-shell) { display: grid; gap: 16px; min-width: 0; width: 100%; }
.public-deal :deep(.checkout-shell) * { box-sizing: border-box; }
.public-deal :deep(.checkout-price) { display: flex; justify-content: space-between; align-items: baseline; }
.public-deal :deep(.checkout-price-value) { margin: 0; font-size: 36px; font-weight: 700; color: #f6dfb2; }
.public-deal :deep(.checkout-price-sub) { margin: 0; color: rgba(255,255,255,.68); text-transform: uppercase; letter-spacing: .08em; font-size: 11px; }
.public-deal :deep(.scarcity-row) { display: flex; gap: 8px; flex-wrap: wrap; align-items: center; }
.public-deal :deep(.scarcity-pill) { display: inline-flex; align-items: center; border-radius: 999px; border: 1px solid rgba(255,255,255,.2); padding: 7px 10px; font-size: 12px; color: rgba(255,255,255,.8); }
.public-deal :deep(.scarcity-pill.is-hot) { border-color: rgba(255,170,120,.55); color: #ffd8b2; background: rgba(240,190,100,.14); }
.public-deal :deep(.qty-row) { display: flex; align-items: center; gap: 10px; }
.public-deal :deep(.qty-btn) { width: 42px; height: 42px; border-radius: 12px; border: 1px solid var(--line); background: rgba(255,255,255,.04); color: #dbe5f3; font-size: 21px; transition: transform 160ms ease; }
.public-deal :deep(.qty-btn:hover:not(:disabled)) { transform: translateY(-1px); }
.public-deal :deep(.qty-btn:disabled) { opacity: .45; }
.public-deal :deep(.qty-value) { min-width: 34px; text-align: center; font-size: 22px; font-weight: 600; }
.public-deal :deep(.reserve-pill) { border-radius: 999px; border: 1px solid rgba(113,182,255,.35); background: rgba(113,182,255,.12); color: #a7d5ff; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; padding: 8px 12px; width: fit-content; }
.public-deal :deep(.reserve-pill) { min-height: 34px; display: inline-flex; align-items: center; }
.public-deal :deep(.reserve-pill.is-warning) { border-color: rgba(255,170,120,.55); color: #f4d8a7; background: rgba(240,190,100,.14); box-shadow: 0 0 22px rgba(240,190,100,.24); animation: timerPulse 1.8s ease-in-out infinite; }
@keyframes timerPulse { 0%,100% { transform: scale(1); } 50% { transform: scale(1.015); } }
.public-deal :deep(.checkout-fields) { display: grid !important; grid-template-columns: 1fr !important; gap: 15px !important; min-width: 0; width: 100%; }
.public-deal :deep(.checkout-fields .field) { display: grid !important; grid-template-columns: 1fr !important; gap: 6px !important; min-width: 0; width: 100%; }
.public-deal :deep(.checkout-fields .field > span) { display: block !important; font-size: 12px; letter-spacing: .08em; text-transform: uppercase; color: rgba(255,255,255,.68); line-height: 1.2; }
.public-deal :deep(.checkout-fields .field > input) { display: block !important; box-sizing: border-box; width: 100% !important; min-width: 0 !important; max-width: 100% !important; border-radius: 13px; border: 1px solid var(--line); background: rgba(11,17,28,.7); color: #e8eef8; padding: 13px 12px; min-height: 52px; }
.public-deal :deep(.field--full) { grid-column: span 1 !important; }
.public-deal :deep(.checkout-fields .field > input:focus) { outline: none; border-color: rgba(240,190,100,.45); box-shadow: 0 0 0 2px rgba(240,190,100,.13); }
.form-error { margin: 0; border-radius: 12px; border: 1px solid rgba(255,110,110,.55); background: rgba(120,22,22,.22); color: #ffd0d0; padding: 8px 10px; font-size: 13px; }
.public-deal :deep(.summary-wrap) { border-top: 1px solid rgba(255,255,255,.08); padding-top: 12px; }
.public-deal :deep(.summary) { display: grid; gap: 8px; }
.public-deal :deep(.summary div) { display: flex; align-items: center; justify-content: space-between; color: rgba(255,255,255,.74); }
.public-deal :deep(.summary span) { padding-right: 12px; }
.public-deal :deep(.summary strong) { color: #ecf2fb; }
.public-deal :deep(.summary strong) { min-width: 92px; text-align: right; font-variant-numeric: tabular-nums; }
.public-deal :deep(.summary .total) { margin-top: 6px; border-top: 1px solid var(--line); padding-top: 10px; color: #f4d8a7; font-size: 18px; }
.public-deal :deep(.action-wrap) { display: grid; gap: 12px; }
.public-deal :deep(.checkout-btn) { width: 100%; min-height: 52px; }
.public-deal :deep(.checkout-btn:hover) { filter: brightness(1.06); }
.public-deal :deep(.status-row) { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.public-deal :deep(.status-row) { min-height: 28px; }
.public-deal :deep(.status-chip) { border-radius: 999px; border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.04); color: rgba(255,255,255,.78); font-size: 11px; letter-spacing: .08em; text-transform: uppercase; padding: 6px 10px; }
.public-deal :deep(.status-chip.is-processing) { border-color: rgba(113,182,255,.55); color: #9fd0ff; }
.public-deal :deep(.status-chip.is-success) { border-color: rgba(82,213,139,.58); color: #52d58b; }
.public-deal :deep(.status-chip.is-failed) { border-color: rgba(255,110,110,.55); color: #ffb2b2; }
.public-deal :deep(.status-copy) { color: rgba(255,255,255,.62); font-size: 12px; text-align: right; }
.success-overlay-backdrop {
  position: fixed;
  inset: 0;
  z-index: 70;
  background: rgba(3, 9, 20, 0.62);
  backdrop-filter: blur(12px);
  display: grid;
  place-items: center;
  padding: 18px;
  animation: fadeIn 220ms ease-out both;
}
.success-overlay {
  width: min(100%, 720px);
  max-height: min(88dvh, 920px);
  overflow: auto;
  border-radius: 28px;
  border: 1px solid rgba(120, 226, 168, 0.34);
  background:
    radial-gradient(620px 220px at 50% -10%, rgba(82, 213, 139, 0.16), transparent 56%),
    linear-gradient(165deg, rgba(12, 30, 24, 0.96), rgba(7, 16, 33, 0.98));
  box-shadow: 0 34px 90px rgba(0, 0, 0, 0.5);
  padding: 32px;
  display: grid;
  gap: 20px;
  animation: successPop 260ms cubic-bezier(.2,.8,.2,1) both;
}
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes successPop {
  from { opacity: 0; transform: translateY(14px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
.success-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}
.success-check {
  width: 62px;
  height: 62px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  font-size: 30px;
  font-weight: 800;
  color: #cbffe2;
  border: 1px solid rgba(122, 246, 182, 0.54);
  background: radial-gradient(60% 60% at 45% 35%, rgba(148, 255, 199, 0.28), rgba(69, 172, 114, 0.18));
  box-shadow: 0 0 32px rgba(124, 255, 188, 0.28);
  animation: successPulse 2.2s ease-in-out infinite;
}
@keyframes successPulse {
  0%, 100% { box-shadow: 0 0 20px rgba(124, 255, 188, 0.22); }
  50% { box-shadow: 0 0 38px rgba(124, 255, 188, 0.35); }
}
.success-close {
  border: 1px solid rgba(255,255,255,.18);
  background: rgba(255,255,255,.06);
  color: #d9e7f8;
  border-radius: 11px;
  padding: 8px 11px;
}
.success-badge {
  margin: 0;
  width: fit-content;
  border: 1px solid rgba(122, 246, 182, 0.44);
  background: rgba(122, 246, 182, 0.12);
  color: #d8ffe8;
  border-radius: 999px;
  padding: 6px 10px;
  font-size: 12px;
  letter-spacing: .08em;
  text-transform: uppercase;
}
.success-title {
  margin: 0;
  font-size: clamp(34px, 5vw, 52px);
  line-height: 0.98;
  letter-spacing: -0.03em;
}
.success-sub {
  margin: 0;
  color: rgba(228, 239, 250, 0.78);
  line-height: 1.6;
}
.success-details {
  display: grid;
  gap: 10px;
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 18px;
  background: rgba(7, 19, 35, 0.52);
  padding: 18px;
}
.success-details p {
  margin: 0;
  display: flex;
  justify-content: space-between;
  gap: 16px;
}
.success-details span {
  color: rgba(217, 230, 244, 0.66);
}
.success-details strong {
  color: #eef5ff;
  text-align: right;
}
.success-next {
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 18px;
  background: rgba(6, 14, 26, 0.54);
  padding: 18px;
}
.success-next-title {
  margin: 0 0 10px;
  font-weight: 700;
}
.success-next ul {
  margin: 0;
  padding-left: 18px;
  display: grid;
  gap: 7px;
  color: rgba(223, 235, 248, 0.84);
}
.success-actions {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}
.success-btn {
  border: 1px solid rgba(82,213,139,.5);
  background: rgba(82,213,139,.14);
  color: #d9ffe9;
  border-radius: 12px;
  min-height: 52px;
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
  padding: 14px 16px calc(12px + env(safe-area-inset-bottom, 0px));
}
.sheet-content {
  overflow-y: auto;
  overflow-x: hidden;
  padding: 4px 2px calc(96px + env(safe-area-inset-bottom, 0px));
}
.sheet-handle { width: 56px; height: 5px; border-radius: 999px; background: rgba(255,255,255,.24); margin: 0 auto 10px; }
.sheet-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; }
.sheet-close { border: 1px solid var(--line); background: rgba(255,255,255,.05); color: #dfe8f8; border-radius: 10px; padding: 8px 10px; }
.mobile-sheet .checkout-shell { overflow-y: auto; overflow-x: hidden; padding-bottom: calc(120px + env(safe-area-inset-bottom, 0px)); }
.mobile-sheet .checkout-fields,
.mobile-sheet .checkout-fields .field,
.mobile-sheet .checkout-fields .field > input {
  width: 100% !important;
  min-width: 0 !important;
  max-width: 100% !important;
}
.mobile-sheet .summary-wrap {
  position: sticky;
  bottom: 78px;
  z-index: 2;
  background: linear-gradient(180deg, rgba(9,20,38,0.2), rgba(9,20,38,0.95) 36%);
  padding-top: 14px;
}
.mobile-sheet .action-wrap {
  position: sticky;
  bottom: 0;
  z-index: 3;
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
  .content-grid { grid-template-columns: minmax(0,1fr) minmax(400px, 420px); }
  .checkout-card { min-width: 400px; max-width: 420px; }
}
@media (max-width: 1440px) {
  .page-shell { padding-inline: 32px; }
}
@media (max-width: 1280px) {
  .page-shell { padding-inline: 24px; }
  .content-grid { gap: 16px; }
  .checkout-card { top: 20px; }
  .checkout-price-value { font-size: 34px; }
}
@media (max-width: 1120px) {
  .content-grid { grid-template-columns: 1fr; }
  .desktop-checkout { position: static; max-width: none; min-width: 0; justify-self: stretch; }
}
@media (max-width: 1024px) {
  .hero-img { height: clamp(260px, 34vw, 320px); }
  .page-shell { padding-inline: 24px; }
  .hero-top h1 { font-size: clamp(32px, 5.2vw, 52px); }
  .checkout-shell { gap: 14px; }
  .checkout-price-value { font-size: 32px; }
  .summary div { font-size: 15px; }
}
@media (max-width: 768px) {
  .public-deal { padding-bottom: calc(96px + env(safe-area-inset-bottom, 0px)); }
  .page-shell { padding-inline: 16px; }
  .hero-body { padding: 16px; }
  .content-stack { gap: 14px; }
  .card-inner { padding: 18px; }
  .mobile-sheet { padding: 14px 16px calc(12px + env(safe-area-inset-bottom, 0px)); }
  .mobile-sheet .checkout-shell { padding-bottom: calc(18px + env(safe-area-inset-bottom, 0px)); }
  .trust-row span { font-size: 11px; }
}
@media (max-width: 767px) {
  .public-deal { padding-bottom: calc(94px + env(safe-area-inset-bottom, 0px)); }
  .page-shell { padding-inline: 16px; }
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
@media (max-width: 430px) {
  .page-shell { padding-inline: 14px; }
  .hero-top h1 { font-size: 36px; line-height: 1; }
  .price { font-size: 25px; padding: 8px 11px; }
  .checkout-price-value { font-size: 30px; }
  .checkout-price { gap: 10px; flex-wrap: wrap; }
  .qty-btn { width: 40px; height: 40px; }
  .mobile-cta { left: 8px; right: 8px; gap: 8px; padding: 9px; }
  .mobile-cta-price { font-size: 20px; }
  .mobile-cta-btn { padding: 10px 12px; font-size: 14px; }
  .sheet-head h2 { font-size: 28px; }
  .success-overlay {
    width: 100%;
    height: min(96dvh, 960px);
    max-height: 96dvh;
    border-radius: 24px 24px 0 0;
    align-self: end;
    padding: 24px;
    gap: 18px;
  }
  .success-actions {
    position: sticky;
    bottom: 0;
    grid-template-columns: 1fr;
    background: linear-gradient(180deg, rgba(9,20,38,0.12), rgba(9,20,38,0.94) 42%);
    padding-top: 12px;
    padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px));
  }
  .success-details p { display: grid; gap: 2px; }
  .success-details strong { text-align: left; }
}
@media (max-width: 390px) {
  .page-shell { padding-inline: 12px; }
  .hero-body { padding: 13px; }
  .badge { font-size: 10px; }
  .hero-top h1 { font-size: 32px; }
  .meta-grid p { font-size: 13px; }
  .checkout-card h2 { font-size: 30px; }
  .checkout-shell { gap: 12px; }
  .field input { padding: 12px 10px; min-height: 46px; }
  .summary div { font-size: 14px; }
  .summary .total { font-size: 17px; }
  .mobile-sheet { border-radius: 20px 20px 0 0; }
}
</style>
