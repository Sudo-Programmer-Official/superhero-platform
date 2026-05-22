export type PaymentStatus = "pending" | "paid" | "refunded" | "failed";
export type RedemptionStatus = "active" | "redeemed" | "expired";

export type BookingApiPayload = {
  id: string;
  booking_number: string;
  deal_id: string;
  practitioner_id: string;
  customer_id: string;
  customer_name: string | null;
  customer_email: string;
  customer_phone: string | null;
  avatar_url: string | null;
  quantity: number;
  subtotal: string;
  fee_amount: string;
  total_amount: string;
  currency: string;
  payment_status: string;
  redemption_status: string;
  wallet_pass_id: string | null;
  qr_code: string | null;
  booked_at: string;
  redeemed_at: string | null;
  refunded_at: string | null;
  created_at: string;
  updated_at: string;
};

export type Booking = {
  id: string;
  booking_number: string;
  deal_id: string;
  practitioner_id: string;
  customer_id: string;
  customer_name: string | null;
  customer_email: string;
  customer_phone: string | null;
  avatar_url: string | null;
  quantity: number;
  subtotal: number;
  fee_amount: number;
  total_amount: number;
  currency: string;
  payment_status: PaymentStatus;
  redemption_status: RedemptionStatus;
  wallet_pass_id: string | null;
  qr_code: string | null;
  booked_at: string;
  redeemed_at: string | null;
  refunded_at: string | null;
  created_at: string;
  updated_at: string;
};

export function fromBookingApi(payload: BookingApiPayload): Booking {
  return {
    ...payload,
    subtotal: Number(payload.subtotal || 0),
    fee_amount: Number(payload.fee_amount || 0),
    total_amount: Number(payload.total_amount || 0),
    payment_status: normalizePaymentStatus(payload.payment_status),
    redemption_status: normalizeRedemptionStatus(payload.redemption_status)
  };
}

export function normalizePaymentStatus(value: string): PaymentStatus {
  if (value === "paid" || value === "refunded" || value === "failed") return value;
  return "pending";
}

export function normalizeRedemptionStatus(value: string): RedemptionStatus {
  if (value === "redeemed" || value === "expired") return value;
  return "active";
}

export function getPaymentStatusLabel(value: PaymentStatus): string {
  if (value === "paid") return "Paid";
  if (value === "refunded") return "Refunded";
  if (value === "failed") return "Failed";
  return "Pending";
}

export function getRedemptionStatusLabel(value: RedemptionStatus): string {
  if (value === "redeemed") return "Redeemed";
  if (value === "expired") return "Expired";
  return "Active";
}

export function getPaymentStatusColor(value: PaymentStatus): "green" | "red" | "amber" {
  if (value === "paid") return "green";
  if (value === "failed") return "red";
  return "amber";
}

export function getRedemptionStatusColor(value: RedemptionStatus): "green" | "red" | "amber" {
  if (value === "redeemed") return "green";
  if (value === "expired") return "red";
  return "amber";
}

export function formatBookingMoney(value: number, currency = "USD"): string {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}

export function formatBookingDate(value: string): string {
  return new Date(value).toLocaleString();
}
