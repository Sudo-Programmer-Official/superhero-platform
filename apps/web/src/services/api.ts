import { fromDealApi, type Deal, type DealApiPayload } from "../domain/deal";
import { fromBookingApi, type Booking, type BookingApiPayload } from "../domain/booking";
import type { ActivityEventPage } from "../domain/activity";

export type MePayload = {
  uid: string;
  email: string | null;
  role: string;
  practitioner_id: string | null;
  practitioner_name: string | null;
  practitioner_slug: string | null;
  stripe_account_id: string | null;
  onboarding_state: "not_connected" | "onboarding" | "connected" | "restricted";
  payouts_enabled: boolean;
  charges_enabled: boolean;
};

export type PractitionerPublicPayload = {
  id: string;
  name: string;
  slug: string;
  avatar_url: string | null;
  cover_image_url: string | null;
  logo_url: string | null;
  bio: string | null;
  profile_image: string | null;
  category: string | null;
  tagline: string | null;
  specialties: string[];
  booking_policies: string | null;
  website: string | null;
  support_email: string | null;
  accent_color: string | null;
  verification_state: string;
  social_links: Record<string, string | null>;
  location: string | null;
};

export type PractitionerUpdatePayload = {
  name?: string;
  slug?: string;
  avatar_url?: string | null;
  cover_image_url?: string | null;
  logo_url?: string | null;
  bio?: string | null;
  profile_image?: string | null;
  category?: string | null;
  tagline?: string | null;
  specialties?: string[];
  booking_policies?: string | null;
  website?: string | null;
  support_email?: string | null;
  accent_color?: string | null;
  verification_state?: string | null;
  social_links?: Record<string, string | null>;
  location?: string | null;
};

export type PresignUploadRequest = {
  folder: "practitioners" | "deals" | "wallet-assets" | "branding" | "temp";
  filename: string;
  content_type: string;
  content_length: number;
};

export type PresignUploadResponse = {
  object_key: string;
  upload_url: string;
  content_type: string;
  expires_in: number;
  max_content_length: number;
};

export type FinalizeAssetRequest = {
  target_type: "practitioner" | "deal_card";
  target_id: string;
  field_name: "profile_image" | "image";
  object_key: string;
};

export type UploadPractitionerImageResponse = {
  object_key: string;
  avatar_url: string;
  profile_image: string;
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
  booking_id: string | null;
  deal_id: string;
  owner_id: string;
  customer_id: string;
  qr_code: string;
  pass_status: string;
  redemption_status: string;
  expires_at: string | null;
  source_checkout_session_id: string | null;
  status: string;
  redeemed_at: string | null;
  wallet_provider: string;
  wallet_type: string;
  apple_wallet_url: string | null;
  google_wallet_url: string | null;
  attendee_name: string | null;
  attendee_email: string | null;
  deal_title: string | null;
  booking_number: string | null;
  created_at: string;
};

export class ApiHttpError extends Error {
  status: number;
  detail: unknown;
  constructor(message: string, status: number, detail: unknown) {
    super(message);
    this.name = "ApiHttpError";
    this.status = status;
    this.detail = detail;
  }
}

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

export type CheckoutSessionResultResponse = {
  checkout_session_id: string;
  status: "pending" | "ready";
  wallet_pass_id: string | null;
  booking_id: string | null;
  booking_number: string | null;
  qr_code: string | null;
  apple_wallet_url: string | null;
  google_wallet_url: string | null;
  pass_url: string | null;
};

export type DashboardSummaryPayload = {
  metrics: {
    total_bookings: number;
    revenue: number;
    redemptions: number;
    conversion_rate: number;
  };
  upcoming: Array<{
    id: string;
    title: string;
    image: string | null;
    starts_at: string;
    location: string;
    seats_sold: number;
    capacity: number;
  }>;
};

export type AdminPractitionerRow = {
  id: string;
  name: string;
  slug: string;
  subscription_status: "trial" | "active" | "grace" | "churn_risk" | string;
  payout_status: "connected" | "restricted" | "pending" | string;
  stripe_state: "connected" | "onboarding" | "missing" | string;
  verification_state: "verified" | "pending" | "flagged" | string;
  health: "healthy" | "watch" | "critical" | string;
  is_public: boolean;
  created_at: string;
};

export type AdminDealRow = {
  id: string;
  title: string;
  slug: string;
  practitioner_id: string;
  practitioner_name: string;
  status: "draft" | "published" | "expired" | "archived" | string;
  moderation_state: "clean" | "flagged" | string;
  revenue: string | number;
  bookings_count: number;
  start_time: string;
  created_at: string;
};

export type AdminPayoutRow = {
  id: string;
  practitioner_id: string;
  creator: string;
  amount: string | number;
  status: "pending" | "processing" | "paid" | "failed" | string;
  transfer_state: "queued" | "in_transit" | "completed" | "error" | string;
  transaction_count: number;
  processing_date: string | null;
  payout_date: string | null;
};

export type AdminBookingRow = {
  id: string;
  booking_number: string;
  deal_title: string;
  practitioner_name: string;
  customer_name: string | null;
  customer_email: string;
  quantity: number;
  total_amount: string | number;
  currency: string;
  payment_status: string;
  redemption_status: string;
  wallet_pass_id: string | null;
  created_at: string;
};

export type AdminWalletPassRow = {
  id: string;
  deal_title: string;
  practitioner_name: string;
  attendee_email: string | null;
  booking_number: string | null;
  pass_status: string;
  redemption_status: string;
  wallet_type: string;
  source_checkout_session_id: string | null;
  qr_code: string;
  created_at: string;
};

export type AdminRedemptionRow = {
  wallet_pass_id: string;
  deal_title: string | null;
  practitioner_name: string | null;
  attendee_email: string | null;
  success_count: number;
  failed_count: number;
  duplicate_attempts: number;
  invalid_attempts: number;
  last_event_at: string;
  risk_level: string;
};

export type AdminTimelineEventRow = {
  id: string;
  entity_type: string;
  entity_id: string;
  event_type: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
let onAuthFailureHandler: ((status: 401 | 403) => void) | null = null;

export function setAuthFailureHandler(handler: ((status: 401 | 403) => void) | null): void {
  onAuthFailureHandler = handler;
}

async function checkedFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  const res = await fetch(input, init);
  if (res.status === 401 || res.status === 403) {
    onAuthFailureHandler?.(res.status);
  }
  return res;
}

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
  const res = await checkedFetch(`${API_BASE}/api/v1/me`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed /me: ${res.status}`);
  return res.json() as Promise<MePayload>;
}

export async function bootstrapPractitioner(token: string, name: string): Promise<void> {
  const res = await checkedFetch(`${API_BASE}/api/v1/me/bootstrap-practitioner`, {
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
  const res = await checkedFetch(`${API_BASE}/api/v1/practitioners/${practitionerId}`, {
    method: "PATCH",
    headers: headers(token),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed update practitioner: ${res.status}`);
  return res.json() as Promise<PractitionerPublicPayload>;
}

export async function presignUpload(token: string, payload: PresignUploadRequest): Promise<PresignUploadResponse> {
  const res = await checkedFetch(`${API_BASE}/api/v1/storage/presign-upload`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed presign upload: ${res.status}`);
  return res.json() as Promise<PresignUploadResponse>;
}

export async function uploadFileToPresignedUrl(uploadUrl: string, file: File, contentType: string): Promise<void> {
  const res = await checkedFetch(uploadUrl, {
    method: "PUT",
    headers: {
      "Content-Type": contentType
    },
    body: file
  });
  if (!res.ok) throw new Error(`Failed upload binary: ${res.status}`);
}

export async function finalizeAsset(token: string, payload: FinalizeAssetRequest): Promise<void> {
  const res = await checkedFetch(`${API_BASE}/api/v1/storage/finalize-asset`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed finalize asset: ${res.status}`);
}

export async function uploadPractitionerImage(
  token: string,
  practitionerId: string,
  file: File
): Promise<UploadPractitionerImageResponse> {
  const formData = new FormData();
  formData.set("practitioner_id", practitionerId);
  formData.set("file", file);

  const trimmed = token?.trim();
  if (!trimmed) {
    throw new Error("Authentication session expired.");
  }

  const res = await checkedFetch(`${API_BASE}/api/v1/storage/upload-practitioner-image`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${trimmed}`,
    },
    body: formData
  });
  if (!res.ok) throw new Error(`Failed practitioner image upload: ${res.status}`);
  return res.json() as Promise<UploadPractitionerImageResponse>;
}

export async function createCheckoutSession(
  payload: CheckoutSessionCreatePayload
): Promise<CheckoutSessionCreateResponse> {
  const res = await checkedFetch(`${API_BASE}/api/v1/payments/checkout-session`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed checkout session: ${res.status}`);
  return res.json() as Promise<CheckoutSessionCreateResponse>;
}

export async function fetchCheckoutResult(sessionId: string): Promise<CheckoutSessionResultResponse> {
  const res = await checkedFetch(`${API_BASE}/api/v1/payments/checkout-result?session_id=${encodeURIComponent(sessionId)}`);
  if (!res.ok) throw new Error(`Failed checkout result: ${res.status}`);
  return res.json() as Promise<CheckoutSessionResultResponse>;
}

export async function fetchDashboardSummary(token: string): Promise<DashboardSummaryPayload> {
  const res = await checkedFetch(`${API_BASE}/api/v1/dashboard/summary`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed dashboard summary: ${res.status}`);
  return res.json() as Promise<DashboardSummaryPayload>;
}

export async function createDeal(token: string, payload: DealCardCreatePayload): Promise<DealCardPayload> {
  const res = await checkedFetch(`${API_BASE}/api/v1/deal-cards`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error(`Failed create deal: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function listDeals(token: string): Promise<DealCardPayload[]> {
  const res = await checkedFetch(`${API_BASE}/api/v1/deal-cards`, { headers: headers(token) });
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
  const res = await checkedFetch(`${API_BASE}/api/v1/deal-cards/${dealId}`, {
    method: "PATCH",
    headers: headers(token),
    body: JSON.stringify({ status: wireStatus })
  });
  if (!res.ok) throw new Error(`Failed update deal status: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function duplicateDeal(token: string, dealId: string): Promise<DealCardPayload> {
  const res = await checkedFetch(`${API_BASE}/api/v1/deal-cards/${dealId}/duplicate`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({})
  });
  if (!res.ok) throw new Error(`Failed duplicate deal: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function archiveDeal(token: string, dealId: string): Promise<DealCardPayload> {
  const res = await checkedFetch(`${API_BASE}/api/v1/deal-cards/${dealId}/archive`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({})
  });
  if (!res.ok) throw new Error(`Failed archive deal: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function listPublicDeals(practitionerSlug: string): Promise<DealCardPayload[]> {
  const res = await checkedFetch(`${API_BASE}/api/v1/deal-cards/public/${practitionerSlug}`);
  if (!res.ok) throw new Error(`Failed list public deals: ${res.status}`);
  const json = (await res.json()) as DealApiPayload[];
  return json.map(fromDealApi);
}

export async function fetchPublicDeal(practitionerSlug: string, dealSlug: string): Promise<DealCardPayload> {
  const res = await checkedFetch(`${API_BASE}/api/v1/deal-cards/public/${practitionerSlug}/${dealSlug}`);
  if (!res.ok) throw new Error(`Failed public deal: ${res.status}`);
  const json = (await res.json()) as DealApiPayload;
  return fromDealApi(json);
}

export async function fetchPublicPractitioner(practitionerSlug: string): Promise<PractitionerPublicPayload> {
  const res = await checkedFetch(`${API_BASE}/api/v1/practitioners/public/${practitionerSlug}`);
  if (!res.ok) throw new Error(`Failed public practitioner: ${res.status}`);
  return res.json() as Promise<PractitionerPublicPayload>;
}

export async function listWalletPasses(token: string): Promise<WalletPassPayload[]> {
  const res = await checkedFetch(`${API_BASE}/api/v1/wallet-passes`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed wallet pass list: ${res.status}`);
  return res.json() as Promise<WalletPassPayload[]>;
}

export async function redeemWalletPass(token: string, qrCode: string): Promise<WalletPassPayload> {
  const res = await checkedFetch(`${API_BASE}/api/v1/wallet-passes/redeem`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({ qr_code: qrCode })
  });
  if (!res.ok) {
    let detail: unknown = null;
    try {
      const body = (await res.json()) as { detail?: unknown };
      detail = body?.detail ?? null;
    } catch {
      detail = null;
    }
    throw new ApiHttpError(`Failed redeem: ${res.status}`, res.status, detail);
  }
  return res.json() as Promise<WalletPassPayload>;
}

export async function restoreWalletPass(token: string, walletPassId: string): Promise<WalletPassPayload> {
  const res = await checkedFetch(`${API_BASE}/api/v1/wallet-passes/${walletPassId}/restore`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({})
  });
  if (!res.ok) throw new Error(`Failed restore: ${res.status}`);
  return res.json() as Promise<WalletPassPayload>;
}

export async function listBookings(token: string): Promise<BookingPayload[]> {
  const res = await checkedFetch(`${API_BASE}/api/v1/bookings`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed booking list: ${res.status}`);
  const json = (await res.json()) as BookingApiPayload[];
  return json.map(fromBookingApi);
}

export async function listActivityEvents(token: string, cursor?: string): Promise<ActivityEventPage> {
  const params = new URLSearchParams();
  params.set("limit", "40");
  if (cursor) {
    params.set("cursor", cursor);
  }
  const res = await checkedFetch(`${API_BASE}/api/v1/activity-events?${params.toString()}`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed activity events: ${res.status}`);
  return (await res.json()) as ActivityEventPage;
}

export async function listAdminPractitioners(token: string, query?: string): Promise<AdminPractitionerRow[]> {
  const params = new URLSearchParams();
  if (query?.trim()) params.set("query", query.trim());
  const q = params.toString();
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/practitioners${q ? `?${q}` : ""}`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed admin practitioners: ${res.status}`);
  return (await res.json()) as AdminPractitionerRow[];
}

export async function adminPractitionerAction(
  token: string,
  practitionerId: string,
  action: "impersonate" | "suspend" | "activate" | "grant_credits" | "reset_onboarding" | "resend_verification"
): Promise<AdminPractitionerRow> {
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/practitioners/${practitionerId}/actions`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({ action })
  });
  if (!res.ok) throw new Error(`Failed practitioner action: ${res.status}`);
  return (await res.json()) as AdminPractitionerRow;
}

export async function listAdminDeals(token: string, query?: string, dealStatus?: string): Promise<AdminDealRow[]> {
  const params = new URLSearchParams();
  if (query?.trim()) params.set("query", query.trim());
  if (dealStatus?.trim()) params.set("status", dealStatus.trim());
  const q = params.toString();
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/deals${q ? `?${q}` : ""}`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed admin deals: ${res.status}`);
  return (await res.json()) as AdminDealRow[];
}

export async function adminDealAction(
  token: string,
  dealId: string,
  action: "archive" | "unpublish" | "feature" | "moderate"
): Promise<AdminDealRow> {
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/deals/${dealId}/actions`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({ action })
  });
  if (!res.ok) throw new Error(`Failed deal action: ${res.status}`);
  return (await res.json()) as AdminDealRow;
}

export async function listAdminPayouts(token: string, query?: string, payoutStatus?: string): Promise<AdminPayoutRow[]> {
  const params = new URLSearchParams();
  if (query?.trim()) params.set("query", query.trim());
  if (payoutStatus?.trim()) params.set("status", payoutStatus.trim());
  const q = params.toString();
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/payouts${q ? `?${q}` : ""}`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed admin payouts: ${res.status}`);
  return (await res.json()) as AdminPayoutRow[];
}

export async function adminPayoutAction(
  token: string,
  practitionerId: string,
  action: "mark_paid" | "retry"
): Promise<AdminPayoutRow> {
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/payouts/${practitionerId}/actions`, {
    method: "POST",
    headers: headers(token),
    body: JSON.stringify({ action })
  });
  if (!res.ok) throw new Error(`Failed payout action: ${res.status}`);
  return (await res.json()) as AdminPayoutRow;
}

export async function listAdminBookings(token: string, query?: string, bookingStatus?: string): Promise<AdminBookingRow[]> {
  const params = new URLSearchParams();
  if (query?.trim()) params.set("query", query.trim());
  if (bookingStatus?.trim()) params.set("status", bookingStatus.trim());
  const q = params.toString();
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/bookings${q ? `?${q}` : ""}`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed admin bookings: ${res.status}`);
  return (await res.json()) as AdminBookingRow[];
}

export async function listAdminWalletPasses(
  token: string,
  query?: string,
  passStatus?: string
): Promise<AdminWalletPassRow[]> {
  const params = new URLSearchParams();
  if (query?.trim()) params.set("query", query.trim());
  if (passStatus?.trim()) params.set("status", passStatus.trim());
  const q = params.toString();
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/wallet-passes${q ? `?${q}` : ""}`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed admin wallet passes: ${res.status}`);
  return (await res.json()) as AdminWalletPassRow[];
}

export async function listAdminRedemptions(
  token: string,
  query?: string,
  window: "24h" | "7d" | "30d" | "all" = "24h"
): Promise<AdminRedemptionRow[]> {
  const params = new URLSearchParams();
  if (query?.trim()) params.set("query", query.trim());
  params.set("window", window);
  const q = params.toString();
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/redemptions${q ? `?${q}` : ""}`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed admin redemptions: ${res.status}`);
  return (await res.json()) as AdminRedemptionRow[];
}

export async function listAdminTimeline(
  token: string,
  entityType: string,
  entityId: string,
  limit = 80
): Promise<AdminTimelineEventRow[]> {
  const params = new URLSearchParams();
  params.set("entity_type", entityType);
  params.set("entity_id", entityId);
  params.set("limit", String(limit));
  const res = await checkedFetch(`${API_BASE}/api/v1/admin/timeline?${params.toString()}`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed admin timeline: ${res.status}`);
  return (await res.json()) as AdminTimelineEventRow[];
}
