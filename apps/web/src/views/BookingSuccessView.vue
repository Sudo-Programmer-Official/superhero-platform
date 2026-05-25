<template>
  <section class="success-page">
    <main class="success-shell">
      <header class="success-head">
        <div class="success-check" aria-hidden="true">✓</div>
        <button type="button" class="close-btn" @click="backToDeal">Close</button>
      </header>

      <p class="success-badge">Reservation secured</p>
      <h1>Booking confirmed</h1>
      <p class="lead">Your reservation is secured and confirmation details are on the way.</p>

      <section class="detail-card">
        <p><span>Booking number</span><strong>{{ bookingNumber || "Generating..." }}</strong></p>
        <p><span>Event</span><strong>{{ deal?.title || "OpenMat experience" }}</strong></p>
        <p><span>Date</span><strong>{{ deal ? formatDate(deal.start_time) : "TBD" }}</strong></p>
        <p><span>Attendee</span><strong>{{ attendeeName || "Guest attendee" }}</strong></p>
        <p><span>Confirmation email</span><strong>{{ attendeeEmail || "Email will be delivered shortly" }}</strong></p>
      </section>

      <p class="pass-state" :class="{ ready: isPassReady }">
        {{ isPassReady ? "Pass and QR are ready." : "Preparing pass and QR. This usually takes a few seconds." }}
      </p>

      <section class="next-card">
        <p class="next-title">What happens next</p>
        <ul>
          <li>Confirmation email sent</li>
          <li>QR pass ready for entry</li>
          <li>Show this QR at check-in</li>
          <li>Reminder notifications enabled</li>
        </ul>
      </section>

      <div class="actions">
        <button type="button" class="btn" :disabled="!walletPassUrl" @click="openPass">View Pass</button>
        <button type="button" class="btn" :disabled="!qrCode" @click="downloadQr">Download QR</button>
        <button type="button" class="btn" :disabled="!walletPassUrl" @click="addToWallet">Add to Wallet</button>
        <button type="button" class="btn secondary" @click="goHome">Return Home</button>
      </div>
    </main>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useRoute, useRouter } from "vue-router";
import { formatLocalDateTime, formatTimezone } from "../domain/deal";
import { fetchCheckoutResult, fetchPublicDeal, type DealCardPayload } from "../services/api";
import { showToast } from "../stores/toast";

const route = useRoute();
const router = useRouter();

const deal = ref<DealCardPayload | null>(null);
const walletPassUrl = ref<string | null>(null);
const qrCode = ref<string | null>(null);
const bookingNumber = ref<string | null>(null);
const attendeeName = ref<string>("");
const attendeeEmail = ref<string>("");

const sessionId = computed(() => String(route.query.session_id || ""));
const isPassReady = computed(() => Boolean(walletPassUrl.value || qrCode.value));

function formatDate(value: string): string {
  const tz = deal.value?.timezone || "UTC";
  return `${formatLocalDateTime(value, tz)} ${formatTimezone(value, tz)}`;
}

function backToDeal() {
  router.push({
    name: "public-deal",
    params: {
      practitionerSlug: String(route.params.practitionerSlug || ""),
      dealSlug: String(route.params.dealSlug || "")
    }
  });
}

function goHome() {
  router.push(`/openmat/${String(route.params.practitionerSlug || "")}`);
}

function openPass() {
  if (walletPassUrl.value) {
    window.open(walletPassUrl.value, "_blank", "noopener,noreferrer");
    return;
  }
  showToast("Pass link will appear as soon as issuance completes.", "loading", 2200);
}

function addToWallet() {
  openPass();
}

function downloadQr() {
  if (!qrCode.value) {
    showToast("QR is being prepared. Check your email shortly.", "loading", 2200);
    return;
  }
  const blob = new Blob([qrCode.value], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = `openmat-qr-${bookingNumber.value || "booking"}.txt`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}

async function syncCheckoutArtifacts() {
  if (!sessionId.value) return;
  let attempts = 0;
  while (attempts < 8) {
    attempts += 1;
    const result = await fetchCheckoutResult(sessionId.value);
    if (result.status === "ready") {
      walletPassUrl.value = result.pass_url;
      qrCode.value = result.qr_code;
      bookingNumber.value = result.booking_number;
      return;
    }
    await new Promise((resolve) => window.setTimeout(resolve, 1500));
  }
}

onMounted(async () => {
  const practitionerSlug = String(route.params.practitionerSlug || "");
  const dealSlug = String(route.params.dealSlug || "");
  try {
    deal.value = await fetchPublicDeal(practitionerSlug, dealSlug);
  } catch {
    // Keep success page available even if deal refresh fails.
  }

  try {
    const raw = window.localStorage.getItem("openmat:last-checkout-success");
    if (raw) {
      const parsed = JSON.parse(raw) as { email?: string | null; name?: string | null };
      attendeeEmail.value = parsed.email || "";
      attendeeName.value = parsed.name || "";
    }
  } catch {
    // Ignore invalid local storage payload.
  }

  try {
    await syncCheckoutArtifacts();
  } catch {
    // Do not block success UX on delayed artifact creation.
  }
});
</script>

<style scoped>
.success-page {
  min-height: 100dvh;
  padding: 18px;
  background: radial-gradient(900px 420px at 15% -10%, rgba(38, 91, 169, 0.18), transparent 60%), linear-gradient(180deg, #081a32, #030b18);
  display: grid;
  place-items: center;
}
.success-shell {
  width: min(100%, 760px);
  max-height: min(92dvh, 940px);
  overflow: auto;
  border-radius: 28px;
  border: 1px solid rgba(120, 226, 168, 0.34);
  background: radial-gradient(620px 220px at 50% -10%, rgba(82, 213, 139, 0.16), transparent 56%), linear-gradient(165deg, rgba(12, 30, 24, 0.96), rgba(7, 16, 33, 0.98));
  box-shadow: 0 34px 90px rgba(0, 0, 0, 0.5);
  padding: 32px;
  display: grid;
  gap: 20px;
}
.success-head { display: flex; align-items: center; justify-content: space-between; }
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
}
.close-btn { border: 1px solid rgba(255,255,255,.18); background: rgba(255,255,255,.06); color: #d9e7f8; border-radius: 11px; padding: 8px 11px; }
.success-badge { margin: 0; width: fit-content; border: 1px solid rgba(122, 246, 182, 0.44); background: rgba(122, 246, 182, 0.12); color: #d8ffe8; border-radius: 999px; padding: 6px 10px; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; }
h1 { margin: 0; font-size: clamp(34px, 5vw, 52px); line-height: 0.98; letter-spacing: -0.03em; }
.lead { margin: 0; color: rgba(228, 239, 250, 0.78); line-height: 1.6; }
.detail-card, .next-card { border: 1px solid rgba(255,255,255,.1); border-radius: 18px; padding: 18px; background: rgba(7, 19, 35, 0.52); }
.detail-card { display: grid; gap: 10px; }
.detail-card p { margin: 0; display: flex; justify-content: space-between; gap: 14px; }
.detail-card span { color: rgba(217, 230, 244, 0.66); }
.detail-card strong { color: #eef5ff; text-align: right; }
.pass-state {
  margin: -6px 0 0;
  border: 1px solid rgba(113,182,255,.4);
  background: rgba(113,182,255,.12);
  color: #b9dcff;
  border-radius: 12px;
  padding: 10px 12px;
  font-size: 13px;
  line-height: 1.45;
}
.pass-state.ready {
  border-color: rgba(82,213,139,.46);
  background: rgba(82,213,139,.12);
  color: #c7ffe2;
}
.next-title { margin: 0 0 10px; font-weight: 700; }
.next-card ul { margin: 0; padding-left: 18px; display: grid; gap: 7px; color: rgba(223, 235, 248, 0.84); }
.actions { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.btn { border: 1px solid rgba(82,213,139,.5); background: rgba(82,213,139,.14); color: #d9ffe9; border-radius: 12px; min-height: 52px; padding: 10px 12px; font-weight: 600; }
.btn:disabled { opacity: 0.52; cursor: not-allowed; }
.btn.secondary { border-color: rgba(255,255,255,.18); background: rgba(255,255,255,.06); color: #e8eef8; }
@media (max-width: 768px) {
  .success-page { padding: 0; }
  .success-shell {
    width: 100%;
    height: min(96dvh, 960px);
    max-height: 96dvh;
    border-radius: 24px 24px 0 0;
    align-self: end;
    padding: 24px;
  }
  .actions {
    position: sticky;
    bottom: 0;
    grid-template-columns: 1fr;
    background: linear-gradient(180deg, rgba(9,20,38,0.12), rgba(9,20,38,0.94) 42%);
    padding-top: 12px;
    padding-bottom: calc(8px + env(safe-area-inset-bottom, 0px));
  }
}
</style>
