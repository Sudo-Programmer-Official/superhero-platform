export type PayoutStatus = "pending" | "processing" | "paid" | "failed" | "refunded";

export type Payout = {
  id: string;
  practitioner_id: string;
  amount: number;
  currency: string;
  payout_status: PayoutStatus;
  payout_provider: "stripe" | "internal";
  payout_method: string;
  payout_date: string | null;
  processing_date: string | null;
  created_at: string;
  transaction_count: number;
  notes: string | null;
};

export type PayoutTransactionStatus = "pending" | "processing" | "paid" | "failed" | "refunded";

export type PayoutTransaction = {
  id: string;
  customer: string;
  deal: string;
  gross: number;
  platform_fees: number;
  stripe_fees: number;
  net: number;
  status: PayoutTransactionStatus;
  payout_batch: string;
  created_at: string;
};

export function payoutStatusLabel(status: PayoutStatus): string {
  if (status === "processing") return "Processing";
  if (status === "paid") return "Paid";
  if (status === "failed") return "Failed";
  if (status === "refunded") return "Refunded";
  return "Pending";
}

export function payoutStatusTone(status: PayoutStatus): "green" | "amber" | "red" | "cyan" {
  if (status === "paid") return "green";
  if (status === "failed" || status === "refunded") return "red";
  if (status === "processing") return "cyan";
  return "amber";
}

export function formatPayoutMoney(value: number, currency = "USD"): string {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value);
}
