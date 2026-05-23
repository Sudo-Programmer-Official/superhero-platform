export type ActivityEvent = {
  id: string;
  actor_id: string | null;
  entity_type: string;
  entity_id: string;
  event_type: string;
  metadata: Record<string, unknown>;
  created_at: string;
};

export type ActivityEventPage = {
  items: ActivityEvent[];
  next_cursor: string | null;
};

export function activityLabel(event: ActivityEvent): string {
  const m = event.metadata || {};
  if (event.event_type === "deal.created") return `Deal created: ${String(m.title || event.entity_id)}`;
  if (event.event_type === "deal.published") return `Deal published: ${String(m.title || event.entity_id)}`;
  if (event.event_type === "deal.archived") return `Deal archived: ${String(m.title || event.entity_id)}`;
  if (event.event_type === "deal.duplicated") return `Deal duplicated`;
  if (event.event_type === "booking.created") return `Booking created: ${String(m.booking_number || event.entity_id)}`;
  if (event.event_type === "booking.paid") return `Booking paid`;
  if (event.event_type === "booking.refunded") return `Booking refunded`;
  if (event.event_type === "wallet.generated") return "Wallet pass generated";
  if (event.event_type === "wallet.redeemed") return "Wallet pass redeemed";
  if (event.event_type === "redemption.success") return "Redemption success";
  if (event.event_type === "redemption.failed") return `Redemption failed: ${String(m.reason || "unknown")}`;
  return event.event_type;
}

export function activityTime(value: string): string {
  const deltaMs = Date.now() - new Date(value).getTime();
  const mins = Math.floor(deltaMs / 60000);
  if (mins < 1) return "just now";
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}
