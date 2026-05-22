import { fromDealApi, type Deal, type DealApiPayload } from "../domain/deal";
import { fromBookingApi, type Booking, type BookingApiPayload } from "../domain/booking";
import type { ActivityEvent } from "../domain/activity";

export type MePayload = {
  uid: string;
  email: string | null;
  role: string;
  practitioner_id: string | null;
  practitioner_name: string | null;
  practitioner_slug: string | null;
};

export type PractitionerPublicPayload = {
  id: string;
  name: string;
  slug: string;
  bio: string | null;
  profile_image: string | null;
  location: string | null;
};

export type PractitionerUpdatePayload = {
  name?: string;
  bio?: string | null;
  profile_image?: string | null;
  location?: string | null;
};

export type DealCardCreatePayload = {
  practitioner_id: string;
  title: string;
  cta_text?: string | null;
  booking_url?: string | null;
  description?: string | null;
  image?: string | null;
  price: string;
  capacity: number;
  location: string;
  timezone?: string;
  start_time: string;
  end_time: string;
  expiration_time?: string | null;
  wallet_enabled?: boolean;
};

export type DealCardPayload = Deal;
export type BookingPayload = Booking;

export type WalletPassPayload = {
  id: string;
  deal_id: string;
  customer_id: string;
  qr_code: string;
  source_checkout_session_id: string | null;
  status: string;
  redeemed_at: string | null;
  wallet_type: string;
  created_at: string;
};

export type CheckoutSessionCreatePayload = {
  deal_id: string;
  customer_email: string;
  customer_name?: string;
  quantity?: number;
  success_url: string;
  cancel_url: string;
};

export type CheckoutSessionCreateResponse = {
  checkout_session_id: string;
  checkout_url: string;
};

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function headers(token: string): HeadersInit {
  const trimmed = token?.trim();
  if (!trimmed) {
    throw new Error("Authentication session expired.");
  }
  console.groupCollapsed("API AUTH");
  console.log("hasToken", Boolean(trimmed));
  console.log("tokenPrefix", trimmed.slice(0, 20));
  console.groupEnd();
  return {
    Authorization: `Bearer ${trimmed}`,
    "Content-Type": "application/json"
  };
}

export async function fetchMe(token: string): Promise<MePayload> {
  const res = await fetch(`${API_BASE}/api/v1/me`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed /me: ${res.status}`);
  return res.json() as Promise<MePayload>;
}

export async function bootstrapPractitioner(token: string, name: string): Promise<void> {
  const res = await fetch(`${API_BASE}/api/v1/me/bootstrap-practitioner`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({ name })
  });
  if (!res.ok) throw new Error(`Failed bootstrap: ${res.status}`);
}

export async function updatePractitioner(
  token: string,
  practitionerId: string,
  payload: PractitionerUpdatePayload
): Promise<PractitionerPublicPayload> {
  const res = await fetch(`${API_BASE}/api/v1/practitioners/${practitionerId}`, {
    method: "PATCH",
    headers: headers(token),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed update practitioner: ${res.status}`);
  return res.json() as Promise<PractitionerPublicPayload>;
}

export async function createCheckoutSession(
  payload: CheckoutSessionCreatePayload
): Promise<CheckoutSessionCreateResponse> {
  const res = await fetch(`${API_BASE}/api/v1/payments/checkout-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed checkout session: ${res.status}`);
  return res.json() as Promise<CheckoutSessionCreateResponse>;
}

export async function createDeal(token: string, payload: DealCardCreatePayload): Promise<DealCardPayload> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed create deal: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function listDeals(token: string): Promise<DealCardPayload[]> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed list deals: ${res.status}`);
  const json = (await res.json()) as DealApiPayload[];
  return json.map(fromDealApi);
}

export async function updateDealStatus(
  token: string,
  dealId: string,
  status: "draft" | "published" | "expired" | "archived"
): Promise<DealCardPayload> {
  const wireStatus = status === "archived" ? "canceled" : status;
  const res = await fetch(`${API_BASE}/api/v1/deal-cards/${dealId}`, {
    method: "PATCH",
    headers: headers(token),
    body: JSON.stringify({ status: wireStatus })
  });
  if (!res.ok) throw new Error(`Failed update deal status: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function duplicateDeal(token: string, dealId: string): Promise<DealCardPayload> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards/${dealId}/duplicate`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({})
  });
  if (!res.ok) throw new Error(`Failed duplicate deal: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function archiveDeal(token: string, dealId: string): Promise<DealCardPayload> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards/${dealId}/archive`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({})
  });
  if (!res.ok) throw new Error(`Failed archive deal: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function listPublicDeals(practitionerSlug: string): Promise<DealCardPayload[]> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards/public/${practitionerSlug}`);
  if (!res.ok) throw new Error(`Failed list public deals: ${res.status}`);
  const json = (await res.json()) as DealApiPayload[];
  return json.map(fromDealApi);
}

export async function fetchPublicDeal(practitionerSlug: string, dealSlug: string): Promise<DealCardPayload> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards/public/${practitionerSlug}/${dealSlug}`);
  if (!res.ok) throw new Error(`Failed public deal: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function fetchPublicPractitioner(practitionerSlug: string): Promise<PractitionerPublicPayload> {
  const res = await fetch(`${API_BASE}/api/v1/practitioners/public/${practitionerSlug}`);
  if (!res.ok) throw new Error(`Failed public practitioner: ${res.status}`);
  return res.json() as Promise<PractitionerPublicPayload>;
}

export async function listWalletPasses(token: string): Promise<WalletPassPayload[]> {
  const res = await fetch(`${API_BASE}/api/v1/wallet-passes`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed wallet pass list: ${res.status}`);
  return res.json() as Promise<WalletPassPayload[]>;
}

export async function redeemWalletPass(token: string, qrCode: string): Promise<WalletPassPayload> {
  const res = await fetch(`${API_BASE}/api/v1/wallet-passes/redeem`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({ qr_code: qrCode })
  });
  if (!res.ok) throw new Error(`Failed redeem: ${res.status}`);
  return res.json() as Promise<WalletPassPayload>;
}

export async function restoreWalletPass(token: string, walletPassId: string): Promise<WalletPassPayload> {
  const res = await fetch(`${API_BASE}/api/v1/wallet-passes/${walletPassId}/restore`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({})
  });
  if (!res.ok) throw new Error(`Failed restore: ${res.status}`);
  return res.json() as Promise<WalletPassPayload>;
}

export async function listBookings(token: string): Promise<BookingPayload[]> {
  const res = await fetch(`${API_BASE}/api/v1/bookings`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed booking list: ${res.status}`);
  const json = (await res.json()) as BookingApiPayload[];
  return json.map(fromBookingApi);
}

export async function listActivityEvents(token: string): Promise<ActivityEvent[]> {
  const res = await fetch(`${API_BASE}/api/v1/activity-events`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed activity events: ${res.status}`);
  return (await res.json()) as ActivityEvent[];
}
