<template>
  <DashboardPageShell
    eyebrow="Settings"
    title="Operational Control Center"
    subtitle="Secure and tune account, notifications, security, redemption, integrations, and billing behavior."
  >
    <template #actions>
      <AppButton variant="secondary" size="form" :disabled="saving" @click="saveNow">{{ saving ? "Saving..." : "Save" }}</AppButton>
    </template>

    <div class="settings-layout">
      <aside class="settings-nav">
        <button v-for="section in sections" :key="section.id" class="nav-item" @click="scrollTo(section.id)">{{ section.label }}</button>
      </aside>

      <section class="settings-main">
        <PaddedSectionCard v-if="loading" muted>Loading settings…</PaddedSectionCard>

        <template v-else>
          <PaddedSectionCard id="account">
            <div class="section-head"><h3>Account</h3><span class="save-indicator">{{ saveState }}</span></div>
            <div class="grid-2">
              <label class="field"><span>Display Name</span><AppInput v-model="account.display_name" placeholder="Your name" /></label>
              <label class="field"><span>Email</span><AppInput v-model="account.email" placeholder="you@example.com" /></label>
              <label class="field"><span>Business Name</span><AppInput v-model="account.business_name" placeholder="OpenMat Studio" /></label>
              <label class="field"><span>Public Slug</span><AppInput v-model="account.public_slug" placeholder="marla" /></label>
              <label class="field"><span>Timezone</span><AppInput v-model="account.timezone" /></label>
              <label class="field"><span>Currency</span><AppInput v-model="account.currency" /></label>
              <label class="field"><span>Language</span><AppInput v-model="account.language" /></label>
              <label class="field"><span>Profile Visibility</span>
                <select v-model="settings.profile_visibility" class="input"><option value="public">Public</option><option value="private">Private</option></select>
              </label>
            </div>
          </PaddedSectionCard>

          <PaddedSectionCard id="notifications">
            <h3>Notifications</h3>
            <div class="toggle-grid">
              <ToggleRow label="Email Notifications" v-model="settings.email_notifications" />
              <ToggleRow label="SMS Notifications" v-model="settings.sms_notifications" />
              <ToggleRow label="Booking Alerts" v-model="settings.booking_notifications" />
              <ToggleRow label="Redemption Alerts" v-model="settings.redemption_notifications" />
              <ToggleRow label="Payout Alerts" v-model="settings.payout_notifications" />
              <ToggleRow label="Marketing Emails" v-model="settings.marketing_notifications" />
            </div>
          </PaddedSectionCard>

          <PaddedSectionCard id="appearance">
            <h3>Appearance</h3>
            <div class="grid-2">
              <label class="field"><span>Theme</span>
                <select v-model="settings.appearance_theme" class="input"><option value="dark">Dark</option><option value="light">Light</option><option value="system">System</option></select>
              </label>
              <label class="field"><span>Dashboard Density</span>
                <select v-model="settings.dashboard_density" class="input"><option value="comfortable">Comfortable</option><option value="compact">Compact</option></select>
              </label>
              <ToggleRow label="Card Animations" v-model="settings.card_animations" />
              <label class="field"><span>Session Timeout (mins)</span><AppInput v-model="settings.session_timeout_minutes" type="number" /></label>
            </div>
          </PaddedSectionCard>

          <PaddedSectionCard id="security">
            <h3>Security</h3>
            <div class="security-actions">
              <AppButton variant="secondary">Change Password</AppButton>
              <ToggleRow label="Two-factor Authentication" v-model="settings.two_factor_enabled" />
            </div>
            <div class="session-list">
              <article v-for="session in sessionHistory" :key="session.device + session.at" class="session-item">
                <p>{{ session.device }}</p>
                <span>{{ session.location }} · {{ new Date(session.at).toLocaleString() }}</span>
              </article>
            </div>
          </PaddedSectionCard>

          <PaddedSectionCard id="wallet">
            <h3>Wallet & Redemption</h3>
            <div class="toggle-grid">
              <ToggleRow label="Auto-publish Wallet Passes" v-model="settings.auto_publish_wallet_passes" />
              <ToggleRow label="Public Profile Enabled" v-model="settings.public_profile_enabled" />
            </div>
            <label class="field"><span>Default Redemption Mode</span>
              <select v-model="settings.default_redemption_mode" class="input"><option value="qr">QR</option><option value="nfc">NFC</option><option value="manual">Manual</option></select>
            </label>
          </PaddedSectionCard>

          <PaddedSectionCard id="integrations">
            <h3>Integrations</h3>
            <div class="integration-grid">
              <article v-for="integration in integrations" :key="integration.key" class="integration-card">
                <div>
                  <p class="integration-title">{{ integration.title }}</p>
                  <p class="integration-copy">{{ integration.description }}</p>
                </div>
                <div class="integration-foot">
                  <span class="badge" :class="`is-${integration.status}`">{{ integration.status.replace("_", " ") }}</span>
                  <AppButton variant="ghost" :disabled="integration.status === 'coming_soon'">{{ integration.cta }}</AppButton>
                </div>
              </article>
            </div>
          </PaddedSectionCard>

          <PaddedSectionCard id="billing">
            <h3>Billing & Subscription</h3>
            <div class="billing-grid">
              <p><span>Plan</span><strong>{{ billing.current_plan }}</strong></p>
              <p><span>Renewal</span><strong>{{ new Date(billing.renewal_date).toLocaleDateString() }}</strong></p>
              <p><span>Deals</span><strong>{{ billing.usage.deals }}</strong></p>
              <p><span>Bookings</span><strong>{{ billing.usage.bookings }}</strong></p>
              <p><span>Wallet Passes</span><strong>{{ billing.usage.wallet_passes }}</strong></p>
            </div>
            <div class="billing-actions">
              <AppButton variant="primary">Upgrade Plan</AppButton>
              <AppButton variant="ghost">Invoices</AppButton>
            </div>
          </PaddedSectionCard>

          <PaddedSectionCard id="danger" class="danger-zone">
            <h3>Danger Zone</h3>
            <p>Irreversible account and workspace operations.</p>
            <div class="danger-actions">
              <AppButton variant="ghost">Archive Account</AppButton>
              <AppButton variant="ghost">Export Data</AppButton>
              <AppButton variant="ghost">Delete Workspace</AppButton>
            </div>
          </PaddedSectionCard>
        </template>
      </section>
    </div>
  </DashboardPageShell>
</template>

<script setup lang="ts">
import { computed, defineComponent, h, onMounted } from "vue";
import DashboardPageShell from "../design-system/patterns/DashboardPageShell.vue";
import PaddedSectionCard from "../design-system/patterns/PaddedSectionCard.vue";
import AppButton from "../design-system/primitives/AppButton.vue";
import AppInput from "../design-system/primitives/AppInput.vue";
import { useAccountSettings } from "../composables/useAccountSettings";
import { fetchPublicPractitioner, updatePractitioner } from "../services/api";
import { sessionState } from "../stores/session";

const ToggleRow = defineComponent({
  name: "ToggleRow",
  props: {
    label: { type: String, required: true },
    modelValue: { type: Boolean, required: true }
  },
  emits: ["update:modelValue"],
  setup(props, { emit }) {
    return () =>
      h("label", { class: "toggle-row" }, [
        h("span", props.label),
        h("button", {
          class: ["toggle", props.modelValue ? "is-on" : ""],
          type: "button",
          onClick: () => emit("update:modelValue", !props.modelValue)
        })
      ]);
  }
});

const sections = [
  { id: "account", label: "Account" },
  { id: "notifications", label: "Notifications" },
  { id: "appearance", label: "Appearance" },
  { id: "security", label: "Security" },
  { id: "wallet", label: "Wallet & Redemption" },
  { id: "integrations", label: "Integrations" },
  { id: "billing", label: "Billing" },
  { id: "danger", label: "Danger Zone" }
];

const {
  account,
  billing,
  initialize,
  integrations,
  loading,
  saveAll,
  saveState,
  saving,
  sessionHistory,
  settings
} = useAccountSettings();

const practitionerSlug = computed(() => sessionState.me?.practitioner_slug || "");

function scrollTo(id: string) {
  const el = document.getElementById(id);
  el?.scrollIntoView({ behavior: "smooth", block: "start" });
}

async function saveNow() {
  if (!sessionState.token || !sessionState.me?.practitioner_id) return;
  await saveAll((payload) => updatePractitioner(sessionState.token!, sessionState.me!.practitioner_id!, payload));
}

onMounted(async () => {
  await initialize(async () => {
    if (!practitionerSlug.value) return null;
    try {
      return await fetchPublicPractitioner(practitionerSlug.value);
    } catch {
      return null;
    }
  });
});
</script>

<style scoped>
.settings-layout { display: grid; grid-template-columns: 220px 1fr; gap: 20px; }
.settings-nav { position: sticky; top: 24px; align-self: start; display: grid; gap: 8px; }
.nav-item { min-height: 42px; border-radius: 12px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.03); color: rgba(255,255,255,.8); text-align: left; padding: 0 12px; }
.settings-main { display: grid; gap: 20px; }
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.section-head h3 { margin: 0; font-size: 24px; }
.save-indicator { color: #f4d8a7; font-size: 13px; }
.grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
.field { display: grid; gap: 8px; }
.field span { font-size: 12px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.62); }
.input { min-height: 46px; border-radius: 12px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,18,30,.62); color: #dbe5f3; padding: 0 12px; }
.toggle-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
:deep(.toggle-row) { min-height: 56px; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 0 12px; display: flex; align-items: center; justify-content: space-between; gap: 12px; }
:deep(.toggle-row span) { font-size: 14px; color: rgba(255,255,255,.86); }
:deep(.toggle) { width: 46px; height: 26px; border-radius: 999px; border: 1px solid rgba(255,255,255,.2); background: rgba(255,255,255,.08); position: relative; }
:deep(.toggle::after) { content: ""; position: absolute; top: 3px; left: 3px; width: 18px; height: 18px; border-radius: 999px; background: #fff; transition: transform 180ms ease; }
:deep(.toggle.is-on) { background: rgba(240,190,100,.35); border-color: rgba(240,190,100,.6); }
:deep(.toggle.is-on::after) { transform: translateX(20px); }
.security-actions { display: grid; gap: 12px; margin-bottom: 12px; }
.session-list { display: grid; gap: 10px; }
.session-item { border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 10px 12px; }
.session-item p { margin: 0; font-size: 14px; }
.session-item span { display: block; margin-top: 4px; font-size: 12px; color: rgba(255,255,255,.58); }
.integration-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; }
.integration-card { border-radius: 14px; border: 1px solid rgba(255,255,255,.12); background: rgba(255,255,255,.02); padding: 14px; display: grid; gap: 10px; }
.integration-title { margin: 0; font-size: 18px; }
.integration-copy { margin: 6px 0 0; color: rgba(255,255,255,.64); font-size: 13px; }
.integration-foot { display: flex; justify-content: space-between; align-items: center; gap: 10px; }
.badge { border-radius: 999px; border: 1px solid rgba(255,255,255,.16); padding: 5px 9px; font-size: 11px; text-transform: uppercase; letter-spacing: .08em; }
.badge.is-connected { color: #52d58b; border-color: rgba(82,213,139,.45); }
.badge.is-not_connected { color: #f4d8a7; border-color: rgba(240,190,100,.45); }
.badge.is-coming_soon { color: #9fd0ff; border-color: rgba(113,182,255,.45); }
.billing-grid { display: grid; grid-template-columns: repeat(5, minmax(0,1fr)); gap: 12px; }
.billing-grid p { margin: 0; border-radius: 12px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 12px; display: grid; gap: 5px; }
.billing-grid span { font-size: 11px; text-transform: uppercase; letter-spacing: .08em; color: rgba(255,255,255,.58); }
.billing-grid strong { font-size: 16px; }
.billing-actions { margin-top: 14px; display: flex; gap: 10px; }
.danger-zone { border-color: rgba(255,120,120,.42); background: linear-gradient(180deg, rgba(68,23,23,.2), rgba(46,16,16,.14)); }
.danger-actions { margin-top: 10px; display: flex; flex-wrap: wrap; gap: 10px; }
@media (max-width: 1200px) {
  .settings-layout { grid-template-columns: 1fr; }
  .settings-nav { position: static; grid-template-columns: repeat(4, minmax(0,1fr)); }
  .grid-2, .toggle-grid, .integration-grid { grid-template-columns: 1fr; }
  .billing-grid { grid-template-columns: 1fr 1fr; }
}
@media (max-width: 767px) {
  .settings-nav { grid-template-columns: 1fr 1fr; }
  .billing-grid { grid-template-columns: 1fr; }
  .billing-actions, .danger-actions { flex-direction: column; }
}
</style>
