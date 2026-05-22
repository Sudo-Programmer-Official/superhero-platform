export type DealStatus = "draft" | "published" | "sold_out" | "archived" | "expired";

export type DealApiPayload = {
  id: string;
  slug: string;
  practitioner_id?: string;
  owner_id?: string | null;
  organization_id?: string | null;
  title: string;
  subtitle?: string | null;
  cta_text?: string | null;
  description?: string | null;
  category?: string | null;
  image?: string | null;
  cover_image?: string | null;
  start_time?: string;
  end_time?: string;
  start_at?: string | null;
  end_at?: string | null;
  timezone?: string;
  location?: string;
  location_name?: string | null;
  location_address?: string | null;
  capacity?: number;
  total_seats?: number | null;
  remaining_slots?: number;
  seats_remaining?: number | null;
  sold_count?: number;
  price?: string;
  base_price?: string | null;
  fee_amount?: string;
  total_price?: string | null;
  currency?: string;
  status: string;
  redemption_type?: string;
  share_link?: string | null;
  public_url?: string | null;
  qr_code_url?: string | null;
  views?: number;
  conversions?: number;
  revenue?: string;
  created_at: string;
  updated_at?: string;
  published_at?: string | null;
  booking_url?: string | null;
  expiration_time?: string | null;
  wallet_enabled?: boolean;
};

export type Deal = {
  id: string;
  slug: string;
  owner_id: string | null;
  organization_id: string | null;
  title: string;
  subtitle: string | null;
  description: string | null;
  category: string | null;
  cover_image: string | null;
  start_at: string;
  end_at: string;
  timezone: string;
  location_name: string;
  location_address: string | null;
  total_seats: number;
  seats_remaining: number;
  sold_count: number;
  currency: string;
  base_price: number;
  fee_amount: number;
  total_price: number;
  status: DealStatus;
  redemption_type: "qr" | "nfc" | "manual";
  public_url: string | null;
  qr_code_url: string | null;
  views: number;
  conversions: number;
  revenue: number;
  created_at: string;
  updated_at: string;
  published_at: string | null;

  // Compatibility fields (legacy consumers)
  practitioner_id: string | null;
  cta_text: string | null;
  booking_url: string | null;
  image: string | null;
  price: string;
  capacity: number;
  remaining_slots: number;
  location: string;
  start_time: string;
  end_time: string;
  expiration_time: string | null;
  share_link: string | null;
  wallet_enabled: boolean;
};

function normalizeStatus(raw: string, deal: DealApiPayload): DealStatus {
  if (raw === "draft") return "draft";
  if (raw === "expired") return "expired";
  if (raw === "archived" || raw === "canceled") return "archived";
  const seatsRemaining = deal.seats_remaining ?? deal.remaining_slots ?? 0;
  if (raw === "published" && seatsRemaining <= 0) return "sold_out";
  return "published";
}

export function fromDealApi(payload: DealApiPayload): Deal {
  const startAt = payload.start_at || payload.start_time || new Date().toISOString();
  const endAt = payload.end_at || payload.end_time || startAt;
  const totalSeats = payload.total_seats ?? payload.capacity ?? 0;
  const seatsRemaining = payload.seats_remaining ?? payload.remaining_slots ?? totalSeats;
  const soldCount = payload.sold_count ?? Math.max(0, totalSeats - seatsRemaining);
  const basePrice = Number(payload.base_price ?? payload.price ?? 0);
  const feeAmount = Number(payload.fee_amount ?? 0);
  const totalPrice = Number(payload.total_price ?? basePrice + feeAmount);
  const revenue = Number(payload.revenue ?? soldCount * basePrice);
  const status = normalizeStatus(payload.status, payload);

  return {
    id: payload.id,
    slug: payload.slug,
    owner_id: payload.owner_id ?? payload.practitioner_id ?? null,
    organization_id: payload.organization_id ?? null,
    title: payload.title,
    subtitle: payload.subtitle ?? payload.cta_text ?? null,
    description: payload.description ?? null,
    category: payload.category ?? null,
    cover_image: payload.cover_image ?? payload.image ?? null,
    start_at: startAt,
    end_at: endAt,
    timezone: payload.timezone ?? "UTC",
    location_name: payload.location_name ?? payload.location ?? "",
    location_address: payload.location_address ?? null,
    total_seats: totalSeats,
    seats_remaining: seatsRemaining,
    sold_count: soldCount,
    currency: payload.currency ?? "USD",
    base_price: basePrice,
    fee_amount: feeAmount,
    total_price: totalPrice,
    status,
    redemption_type: (payload.redemption_type as "qr" | "nfc" | "manual") || "qr",
    public_url: payload.public_url ?? payload.share_link ?? null,
    qr_code_url: payload.qr_code_url ?? null,
    views: payload.views ?? 0,
    conversions: payload.conversions ?? soldCount,
    revenue,
    created_at: payload.created_at,
    updated_at: payload.updated_at ?? payload.created_at,
    published_at: payload.published_at ?? null,

    practitioner_id: payload.practitioner_id ?? payload.owner_id ?? null,
    cta_text: payload.cta_text ?? payload.subtitle ?? null,
    booking_url: payload.booking_url ?? null,
    image: payload.image ?? payload.cover_image ?? null,
    price: basePrice.toFixed(2),
    capacity: totalSeats,
    remaining_slots: seatsRemaining,
    location: payload.location ?? payload.location_name ?? "",
    start_time: payload.start_time ?? startAt,
    end_time: payload.end_time ?? endAt,
    expiration_time: payload.expiration_time ?? null,
    share_link: payload.share_link ?? payload.public_url ?? null,
    wallet_enabled: payload.wallet_enabled ?? true
  };
}

export function getDealStatus(deal: Pick<Deal, "status" | "end_at" | "seats_remaining">): DealStatus {
  if (deal.status === "draft") return "draft";
  if (deal.status === "archived") return "archived";
  if (deal.status === "sold_out") return "sold_out";
  if (deal.status === "expired") return "expired";
  if (new Date(deal.end_at).getTime() < Date.now()) return "expired";
  if (deal.seats_remaining <= 0) return "sold_out";
  return "published";
}

export function getStatusLabel(status: DealStatus): string {
  if (status === "sold_out") return "Sold Out";
  if (status === "archived") return "Archived";
  if (status === "expired") return "Expired";
  if (status === "published") return "Published";
  return "Draft";
}

export function getStatusColor(status: DealStatus): string {
  if (status === "published") return "green";
  if (status === "draft") return "amber";
  if (status === "sold_out") return "red";
  if (status === "archived") return "slate";
  return "red";
}

export function formatDealDate(value: string): string {
  return new Date(value).toLocaleDateString();
}

export function formatDealTime(value: string): string {
  return new Date(value).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

export function formatRelativeDealTime(value: string): string {
  const delta = new Date(value).getTime() - Date.now();
  const abs = Math.abs(delta);
  const day = 24 * 60 * 60 * 1000;
  if (abs < day) return delta >= 0 ? "today" : "today";
  const days = Math.round(abs / day);
  return delta >= 0 ? `in ${days}d` : `${days}d ago`;
}

export function formatLocalDateTime(value: string, timezone: string): string {
  return new Intl.DateTimeFormat(undefined, {
    weekday: "long",
    month: "long",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZone: timezone
  }).format(new Date(value));
}

export function formatTimezone(value: string, timezone: string): string {
  return new Intl.DateTimeFormat(undefined, {
    timeZone: timezone,
    timeZoneName: "short"
  })
    .formatToParts(new Date(value))
    .find((part) => part.type === "timeZoneName")
    ?.value || timezone;
}

export function formatRelativeTime(value: string): string {
  const ms = new Date(value).getTime() - Date.now();
  const abs = Math.abs(ms);
  const day = 24 * 60 * 60 * 1000;
  if (abs < day) return ms >= 0 ? "today" : "today";
  const days = Math.round(abs / day);
  return ms >= 0 ? `in ${days} days` : `${days} days ago`;
}

export function formatMoney(amount: number, currency = "USD"): string {
  return new Intl.NumberFormat(undefined, {
    style: "currency",
    currency,
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(amount);
}

export function calculateCheckoutTotals(deal: Pick<Deal, "base_price" | "fee_amount" | "currency">, quantity: number): {
  subtotal: number;
  fee: number;
  tax: number;
  total: number;
  formatted: { subtotal: string; fee: string; tax: string; total: string };
} {
  const subtotal = deal.base_price * quantity;
  const fee = (deal.fee_amount || deal.base_price * 0.05) * quantity;
  const tax = subtotal * 0.08;
  const total = subtotal + fee + tax;
  return {
    subtotal,
    fee,
    tax,
    total,
    formatted: {
      subtotal: formatMoney(subtotal, deal.currency),
      fee: formatMoney(fee, deal.currency),
      tax: formatMoney(tax, deal.currency),
      total: formatMoney(total, deal.currency)
    }
  };
}
