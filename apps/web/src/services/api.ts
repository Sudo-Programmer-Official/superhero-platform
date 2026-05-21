export type MePayload = {
  uid: string;
  email: string | null;
  role: string;
  practitioner_id: string | null;
  practitioner_name: string | null;
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
