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
  start_time: string;
  end_time: string;
  expiration_time?: string | null;
  wallet_enabled?: boolean;
};

export type DealCardPayload = {
  id: string;
  practitioner_id: string;
  title: string;
  slug: string;
  cta_text: string | null;
  booking_url: string | null;
  description: string | null;
  image: string | null;
  price: string;
  capacity: number;
  remaining_slots: number;
  location: string;
  start_time: string;
  end_time: string;
  expiration_time: string | null;
  share_link: string | null;
  status: "draft" | "published" | "expired";
  wallet_enabled: boolean;
  created_at: string;
};

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
  success_url: string;
  cancel_url: string;
};

export type CheckoutSessionCreateResponse = {
  checkout_session_id: string;
  checkout_url: string;
};

const API_BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";

function headers(token: string): HeadersInit {
  return {
    Authorization: `Bearer ${token}`,
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
  return res.json() as Promise<DealCardPayload>;
}

export async function listDeals(token: string): Promise<DealCardPayload[]> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards`, { headers: headers(token) });
  if (!res.ok) throw new Error(`Failed list deals: ${res.status}`);
  return res.json() as Promise<DealCardPayload[]>;
}

export async function updateDealStatus(
  token: string,
  dealId: string,
  status: "draft" | "published" | "expired"
): Promise<DealCardPayload> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards/${dealId}`, {
    method: "PATCH",
    headers: headers(token),
    body: JSON.stringify({ status })
  });
  if (!res.ok) throw new Error(`Failed update deal status: ${res.status}`);
  return res.json() as Promise<DealCardPayload>;
}

export async function listPublicDeals(practitionerSlug: string): Promise<DealCardPayload[]> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards/public/${practitionerSlug}`);
  if (!res.ok) throw new Error(`Failed list public deals: ${res.status}`);
  return res.json() as Promise<DealCardPayload[]>;
}

export async function fetchPublicDeal(practitionerSlug: string, dealSlug: string): Promise<DealCardPayload> {
  const res = await fetch(`${API_BASE}/api/v1/deal-cards/public/${practitionerSlug}/${dealSlug}`);
  if (!res.ok) throw new Error(`Failed public deal: ${res.status}`);
  return res.json() as Promise<DealCardPayload>;
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
