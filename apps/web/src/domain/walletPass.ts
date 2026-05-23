export type WalletPassStatus = "active" | "redeemed" | "expired" | "revoked";

export type WalletPassTone = "green" | "amber" | "red" | "cyan";

export function normalizeWalletPassStatus(passStatus: string, redemptionStatus?: string): WalletPassStatus {
  const value = (passStatus || redemptionStatus || "").trim().toLowerCase();
  if (value === "redeemed") return "redeemed";
  if (value === "expired") return "expired";
  if (value === "revoked") return "revoked";
  return "active";
}

export function walletPassStatusLabel(status: WalletPassStatus): string {
  if (status === "redeemed") return "Redeemed";
  if (status === "expired") return "Expired";
  if (status === "revoked") return "Revoked";
  return "Active";
}

export function walletPassStatusTone(status: WalletPassStatus): WalletPassTone {
  if (status === "redeemed") return "green";
  if (status === "expired") return "red";
  if (status === "revoked") return "amber";
  return "cyan";
}

export function walletPassStatusIcon(status: WalletPassStatus): string {
  if (status === "redeemed") return "check";
  if (status === "expired") return "clock";
  if (status === "revoked") return "block";
  return "spark";
}
