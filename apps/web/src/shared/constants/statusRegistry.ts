export type StatusTone = "neutral" | "info" | "success" | "warning" | "danger";

export type StatusConfig = {
  label: string;
  tone: StatusTone;
};

const statusRegistry: Record<string, StatusConfig> = {
  pending: { label: "Pending", tone: "warning" },
  processing: { label: "Processing", tone: "info" },
  active: { label: "Active", tone: "success" },
  archived: { label: "Archived", tone: "neutral" },
  expired: { label: "Expired", tone: "neutral" },
  failed: { label: "Failed", tone: "danger" },
  redeemed: { label: "Redeemed", tone: "success" },
  published: { label: "Published", tone: "success" },
  suspended: { label: "Suspended", tone: "danger" },
  draft: { label: "Draft", tone: "info" },
  connected: { label: "Connected", tone: "success" },
  restricted: { label: "Restricted", tone: "danger" },
  onboarding: { label: "Onboarding", tone: "warning" },
  approval: { label: "Approval", tone: "warning" },
  missing: { label: "Missing", tone: "neutral" },
  verified: { label: "Verified", tone: "success" },
  flagged: { label: "Flagged", tone: "danger" },
  healthy: { label: "Healthy", tone: "success" },
  watch: { label: "Watch", tone: "warning" },
  critical: { label: "Critical", tone: "danger" }
};

export function getStatusConfig(status: string): StatusConfig {
  return statusRegistry[status] || { label: status, tone: "neutral" };
}
