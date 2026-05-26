function envFlag(value: string | boolean | undefined): boolean {
  if (typeof value === "boolean") return value;
  const raw = String(value || "").trim().toLowerCase();
  return raw === "1" || raw === "true" || raw === "yes" || raw === "on";
}

export const OPERATOR_MODE_ENABLED = envFlag(import.meta.env.VITE_OPERATOR_MODE_ENABLED);
