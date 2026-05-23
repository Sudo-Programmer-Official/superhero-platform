import { computed, reactive, ref } from "vue";
import { defaultAccountSettings, type AccountSettings } from "../domain/settings";
import { updatePractitioner, type PractitionerPublicPayload, type PractitionerUpdatePayload } from "../services/api";
import { sessionState } from "../stores/session";

const STORAGE_KEY = "openmat:account-settings:v1";

function readStoredSettings(): AccountSettings {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY);
    if (!raw) return { ...defaultAccountSettings };
    return { ...defaultAccountSettings, ...(JSON.parse(raw) as Partial<AccountSettings>) };
  } catch {
    return { ...defaultAccountSettings };
  }
}

function writeStoredSettings(settings: AccountSettings) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(settings));
}

export function useAccountSettings() {
  const settings = reactive<AccountSettings>(readStoredSettings());
  const loading = ref(true);
  const saving = ref(false);
  const saveState = ref("Ready");
  const account = reactive({
    display_name: "",
    email: "",
    business_name: "",
    public_slug: "",
    timezone: settings.default_timezone,
    currency: settings.default_currency,
    language: settings.language
  });

  const integrations = computed(() => [
    { key: "stripe", title: "Stripe", status: sessionState.me?.stripe_account_id ? "connected" : "not_connected", description: "Payout account and settlement rails.", cta: sessionState.me?.stripe_account_id ? "Manage" : "Connect" },
    { key: "apple_wallet", title: "Apple Wallet", status: "coming_soon", description: "Pass packaging and signing pipeline.", cta: "Coming soon" },
    { key: "google_wallet", title: "Google Wallet", status: "coming_soon", description: "Google wallet pass provisioning.", cta: "Coming soon" },
    { key: "calendar", title: "Calendar Sync", status: "not_connected", description: "Push experiences to external calendars.", cta: "Connect" },
    { key: "mindbody", title: "MindBody", status: "coming_soon", description: "Class inventory and attendance bridge.", cta: "Coming soon" },
    { key: "webhooks", title: "Zapier / Webhooks", status: "coming_soon", description: "Automation hooks for partner workflows.", cta: "Coming soon" }
  ]);

  const billing = computed(() => ({
    current_plan: "Creator Pro",
    renewal_date: new Date(Date.now() + 1000 * 60 * 60 * 24 * 26).toISOString(),
    usage: {
      deals: 12,
      bookings: 248,
      wallet_passes: 196
    }
  }));

  const sessionHistory = computed(() => [
    { device: "MacBook Pro · Chrome", location: "Chicago, US", at: new Date().toISOString() },
    { device: "iPhone · Safari", location: "Chicago, US", at: new Date(Date.now() - 1000 * 60 * 60 * 9).toISOString() },
    { device: "Windows · Edge", location: "Austin, US", at: new Date(Date.now() - 1000 * 60 * 60 * 36).toISOString() }
  ]);

  function hydrateAccountFromProfile(profile: PractitionerPublicPayload | null) {
    account.display_name = sessionState.user?.displayName || "";
    account.email = sessionState.user?.email || sessionState.me?.email || "";
    account.business_name = profile?.name || sessionState.me?.practitioner_name || "";
    account.public_slug = profile?.slug || sessionState.me?.practitioner_slug || "";
    account.timezone = settings.default_timezone;
    account.currency = settings.default_currency;
    account.language = settings.language;
  }

  function saveSettingsOnly() {
    settings.updated_at = new Date().toISOString();
    writeStoredSettings(settings);
  }

  async function saveAll(onPersistAccount: (payload: PractitionerUpdatePayload) => Promise<void>) {
    const snapshot = JSON.parse(JSON.stringify(settings)) as AccountSettings;
    saving.value = true;
    saveState.value = "Saving...";
    try {
      settings.default_timezone = account.timezone;
      settings.default_currency = account.currency;
      settings.language = account.language;
      saveSettingsOnly();
      await onPersistAccount({
        name: account.business_name,
        slug: account.public_slug
      });
      saveState.value = "Saved";
    } catch (err) {
      Object.assign(settings, snapshot);
      saveState.value = `Save failed: ${String(err)}`;
    } finally {
      saving.value = false;
    }
  }

  async function initialize(fetchProfile: () => Promise<PractitionerPublicPayload | null>) {
    loading.value = true;
    try {
      const profile = await fetchProfile();
      hydrateAccountFromProfile(profile);
      saveState.value = "Ready";
    } finally {
      loading.value = false;
    }
  }

  return {
    account,
    billing,
    initialize,
    integrations,
    loading,
    saveAll,
    saveSettingsOnly,
    saveState,
    saving,
    sessionHistory,
    settings
  };
}
