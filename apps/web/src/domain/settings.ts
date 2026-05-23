export type AppearanceTheme = "dark" | "light" | "system";
export type RedemptionMode = "qr" | "nfc" | "manual";

export type AccountSettings = {
  profile_visibility: "public" | "private";
  default_timezone: string;
  default_currency: string;
  language: string;
  email_notifications: boolean;
  sms_notifications: boolean;
  marketing_notifications: boolean;
  booking_notifications: boolean;
  redemption_notifications: boolean;
  payout_notifications: boolean;
  two_factor_enabled: boolean;
  session_timeout_minutes: number;
  appearance_theme: AppearanceTheme;
  public_profile_enabled: boolean;
  auto_publish_wallet_passes: boolean;
  default_redemption_mode: RedemptionMode;
  dashboard_density: "comfortable" | "compact";
  card_animations: boolean;
  updated_at: string;
};

export const defaultAccountSettings: AccountSettings = {
  profile_visibility: "public",
  default_timezone: Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC",
  default_currency: "USD",
  language: "en-US",
  email_notifications: true,
  sms_notifications: false,
  marketing_notifications: true,
  booking_notifications: true,
  redemption_notifications: true,
  payout_notifications: true,
  two_factor_enabled: false,
  session_timeout_minutes: 60,
  appearance_theme: "dark",
  public_profile_enabled: true,
  auto_publish_wallet_passes: true,
  default_redemption_mode: "qr",
  dashboard_density: "comfortable",
  card_animations: true,
  updated_at: new Date().toISOString()
};
