<template>
  <section class="bookings">
    <header class="bookings__head">
      <div>
        <p class="eyebrow">Bookings</p>
        <h1>Transaction Ledger</h1>
        <p>Canonical booking records for checkout, wallet, redemption, and payouts.</p>
      </div>
      <AppButton variant="secondary" size="form" :disabled="loading" @click="load">Refresh</AppButton>
    </header>

    <AppCard v-if="loading" muted>Loading bookings…</AppCard>
    <AppCard v-else-if="errorText" class="error-card">{{ errorText }}</AppCard>

    <AppCard v-else-if="bookings.length === 0" muted>
      <h3>No bookings yet</h3>
      <p>Bookings appear automatically after checkout is paid and wallet pass is issued.</p>
    </AppCard>

    <AppCard v-else class="table-wrap">
      <table class="booking-table">
        <thead>
          <tr>
            <th>Booking</th>
            <th>Customer</th>
            <th>Qty</th>
            <th>Total</th>
            <th>Payment</th>
            <th>Redemption</th>
            <th>Booked at</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="booking in bookings" :key="booking.id">
            <td>
              <p class="mono">{{ booking.booking_number }}</p>
              <p class="sub">Deal {{ booking.deal_id.slice(0, 8) }}</p>
            </td>
            <td>
              <p>{{ booking.customer_name || 'Guest' }}</p>
              <p class="sub">{{ booking.customer_email }}</p>
            </td>
            <td>{{ booking.quantity }}</td>
            <td>{{ formatBookingMoney(booking.total_amount, booking.currency) }}</td>
            <td><span class="chip" :class="`chip--${getPaymentStatusColor(booking.payment_status)}`">{{ getPaymentStatusLabel(booking.payment_status) }}</span></td>
            <td><span class="chip" :class="`chip--${getRedemptionStatusColor(booking.redemption_status)}`">{{ getRedemptionStatusLabel(booking.redemption_status) }}</span></td>
            <td>{{ formatBookingDate(booking.booked_at) }}</td>
          </tr>
        </tbody>
      </table>
    </AppCard>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppCard from "../design-system/primitives/AppCard.vue";
import {
  formatBookingDate,
  formatBookingMoney,
  getPaymentStatusColor,
  getPaymentStatusLabel,
  getRedemptionStatusColor,
  getRedemptionStatusLabel,
  type Booking
} from "../domain/booking";
import { listBookings } from "../services/api";
import { sessionState } from "../stores/session";

const bookings = ref<Booking[]>([]);
const loading = ref(true);
const errorText = ref("");

async function load() {
  if (!sessionState.token) {
    errorText.value = "Authentication session expired.";
    loading.value = false;
    return;
  }
  loading.value = true;
  errorText.value = "";
  try {
    bookings.value = await listBookings(sessionState.token);
  } catch (err) {
    errorText.value = `Failed to load bookings: ${String(err)}`;
  } finally {
    loading.value = false;
  }
}

onMounted(load);
</script>

<style scoped>
.bookings { padding: 18px; display: grid; gap: 12px; }
.bookings__head { display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.bookings__head h1 { margin: 6px 0 0; font-size: clamp(30px, 4vw, 46px); }
.bookings__head p { margin: 8px 0 0; color: rgba(255,255,255,.66); }
.error-card { border: 1px solid rgba(255,100,100,.55); color: #ffd0d0; }
.table-wrap { overflow: auto; }
.booking-table { width: 100%; min-width: 920px; border-collapse: collapse; }
.booking-table th { text-align: left; font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.58); border-bottom: 1px solid rgba(255,255,255,.12); padding: 10px; }
.booking-table td { padding: 10px; border-bottom: 1px solid rgba(255,255,255,.07); color: rgba(255,255,255,.86); }
.mono { margin: 0; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, Liberation Mono, Courier New, monospace; }
.sub { margin: 4px 0 0; color: rgba(255,255,255,.55); font-size: 12px; }
.chip { border-radius: 999px; border: 1px solid rgba(255,255,255,.16); padding: 4px 8px; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.chip--green { color: #52d58b; border-color: rgba(82,213,139,.55); }
.chip--amber { color: #f4d8a7; border-color: rgba(240,190,100,.55); }
.chip--red { color: #ffb5b5; border-color: rgba(255,120,120,.55); }
@media (max-width: 767px) {
  .bookings { padding: 12px; }
  .bookings__head { flex-direction: column; }
}
</style>
