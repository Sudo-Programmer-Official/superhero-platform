<template>
  <DashboardPageShell :eyebrow="sectionEyebrow" :title="sectionTitle" :subtitle="sectionSubtitle">
    <template #actions>
      <AppButton variant="secondary" size="form" @click="refreshCurrent">Refresh</AppButton>
    </template>

    <PaddedSectionCard>
      <div class="section-head">
        <div class="section-head__title">
          <h3>{{ sectionTitle }} Operations</h3>
          <p v-if="selectedCount > 0">{{ selectedCount }} selected</p>
        </div>
        <input v-model="query" class="query" :placeholder="`Search ${sectionTitle}`" />
      </div>
      <AppLoadingState
        v-if="currentLoading"
        :title="`Loading ${sectionTitle} data`"
        description="Syncing operational records and statuses."
      />
      <AppErrorState v-else-if="currentError" title="Operation failed" :description="currentError" />

      <template v-else-if="mode === 'practitioners'">
        <AppDataTable
          :columns="practitionerColumns"
          :rows="practitionerOps.filtered"
          :row-key="(row) => String(row.id)"
          selectable
          @selection-change="handleSelectionChange"
        >
          <template #bulk-actions="{ selectedKeys: keys }">
            <AppButton size="sm" variant="ghost" :disabled="keys.length === 0" @click="bulkPractitionerAction('impersonate', keys)">Impersonate</AppButton>
            <AppButton size="sm" variant="secondary" :disabled="keys.length === 0" @click="confirmBulkAction('Suspend selected practitioners?', 'Bulk suspension changes account visibility and workflows.', () => bulkPractitionerAction('suspend', keys))">Suspend</AppButton>
          </template>
          <template #cell-subscription_status="{ row }"><AppStatusPill :status="String(row.subscription_status)" /></template>
          <template #cell-payout_status="{ row }"><AppStatusPill :status="String(row.payout_status)" /></template>
          <template #cell-stripe_state="{ row }"><AppStatusPill :status="String(row.stripe_state)" /></template>
          <template #cell-verification_state="{ row }"><AppStatusPill :status="String(row.verification_state)" /></template>
          <template #cell-health="{ row }"><AppStatusPill :status="String(row.health)" /></template>
          <template #cell-actions="{ row }">
            <div class="actions">
              <button @click="practitionerOps.performAction('impersonate', String(row.id))">Impersonate</button>
              <button class="danger" @click="confirmAction(`Suspend ${row.name}?`, 'This can impact payouts and visibility.', () => practitionerOps.performAction('suspend', String(row.id)))">Suspend</button>
            </div>
          </template>
          <template #empty><AppEmptyState title="No practitioners" description="No practitioners match the current search or filters." /></template>
        </AppDataTable>
      </template>

      <template v-else-if="mode === 'deals'">
        <AppDataTable
          :columns="dealColumns"
          :rows="dealOps.filtered"
          :row-key="(row) => String(row.id)"
          selectable
          @selection-change="handleSelectionChange"
        >
          <template #bulk-actions="{ selectedKeys: keys }">
            <AppButton size="sm" variant="ghost" :disabled="keys.length === 0" @click="bulkDealAction('moderate', keys)">Moderate</AppButton>
            <AppButton size="sm" variant="secondary" :disabled="keys.length === 0" @click="confirmBulkAction('Archive selected deals?', 'Archived deals are removed from active operations.', () => bulkDealAction('archive', keys))">Archive</AppButton>
          </template>
          <template #cell-status="{ row }"><AppStatusPill :status="String(row.status)" /></template>
          <template #cell-moderation_state="{ row }"><AppStatusPill :status="String(row.moderation_state)" /></template>
          <template #cell-revenue="{ row }">${{ Number(row.revenue).toFixed(2) }}</template>
          <template #cell-actions="{ row }">
            <div class="actions">
              <button class="danger" @click="confirmAction(`Archive ${row.title}?`, 'This hides the deal and can affect active campaigns.', () => dealOps.performAction('archive', String(row.id)))">Archive</button>
              <button class="danger" @click="confirmAction(`Unpublish ${row.title}?`, 'This removes public visibility immediately.', () => dealOps.performAction('unpublish', String(row.id)))">Unpublish</button>
              <button @click="dealOps.performAction('moderate', String(row.id))">Moderate</button>
            </div>
          </template>
          <template #empty><AppEmptyState title="No deals" description="No deals found for the current search scope." /></template>
        </AppDataTable>
      </template>

      <template v-else-if="mode === 'payouts'">
        <AppDataTable
          :columns="payoutColumns"
          :rows="payoutOps.filtered"
          :row-key="(row) => String(row.id)"
          selectable
          @selection-change="handleSelectionChange"
        >
          <template #bulk-actions="{ selectedKeys: keys }">
            <AppButton size="sm" variant="ghost" :disabled="keys.length === 0" @click="bulkPayoutAction('retry', keys)">Retry</AppButton>
            <AppButton size="sm" variant="secondary" :disabled="keys.length === 0" @click="confirmBulkAction('Mark selected payouts as paid?', 'Use only after transfer reconciliation.', () => bulkPayoutAction('mark_paid', keys))">Mark paid</AppButton>
          </template>
          <template #cell-amount="{ row }">${{ Number(row.amount).toFixed(2) }}</template>
          <template #cell-status="{ row }"><AppStatusPill :status="String(row.status)" /></template>
          <template #cell-transfer_state="{ row }"><AppStatusPill :status="String(row.transfer_state)" /></template>
          <template #cell-actions="{ row }">
            <div class="actions">
              <button class="danger" @click="confirmAction(`Mark payout ${row.id} as paid?`, 'Ensure transfer confirmation exists before continuing.', () => payoutOps.markPaid(String(row.id)))">Mark paid</button>
              <button @click="payoutOps.retryPayout(String(row.id))">Retry</button>
            </div>
          </template>
          <template #empty><AppEmptyState title="No payouts" description="No payout batches available in the current scope." /></template>
        </AppDataTable>
      </template>

      <template v-else-if="mode === 'moderation'">
        <AppDataTable
          :columns="moderationColumns"
          :rows="moderation.filtered"
          :row-key="(row) => String(row.id)"
          selectable
          @selection-change="handleSelectionChange"
        >
          <template #bulk-actions="{ selectedKeys: keys }">
            <AppButton size="sm" variant="secondary" :disabled="keys.length === 0" @click="confirmBulkAction('Resolve selected flags?', 'Ensure moderation notes are complete before resolving.', () => bulkModerationResolve(keys))">Resolve selected</AppButton>
          </template>
          <template #cell-severity="{ row }"><AppStatusPill :status="String(row.severity)" /></template>
          <template #cell-state="{ row }"><AppStatusPill :status="String(row.state)" /></template>
          <template #cell-actions="{ row }">
            <div class="actions">
              <button @click="confirmAction(`Resolve flag ${row.id}?`, 'Use this after moderation notes are complete.', () => moderation.resolve(String(row.id)))">Resolve</button>
            </div>
          </template>
          <template #empty><AppEmptyState title="No moderation flags" description="No flagged records in the current moderation queue." /></template>
        </AppDataTable>
      </template>

      <template v-else>
        <div class="placeholder-grid">
          <article v-for="item in placeholders" :key="item.title" class="placeholder-card">
            <h4>{{ item.title }}</h4>
            <p>{{ item.copy }}</p>
            <AppButton variant="ghost">Open {{ item.title }}</AppButton>
          </article>
        </div>
      </template>
    </PaddedSectionCard>

    <AppConfirmModal
      :open="confirmOpen"
      :title="confirmTitle"
      :description="confirmDescription"
      confirm-label="Confirm action"
      @cancel="closeConfirm"
      @confirm="runConfirm"
    />
  </DashboardPageShell>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute } from "vue-router";
import { useDealOps } from "../composables/useDealOps";
import { useModerationCenter } from "../composables/useModerationCenter";
import { usePayoutOps } from "../composables/usePayoutOps";
import { usePractitionerOps } from "../composables/usePractitionerOps";
import AppDataTable from "../../design-system/patterns/AppDataTable.vue";
import AppButton from "../../design-system/primitives/AppButton.vue";
import AppConfirmModal from "../../design-system/primitives/AppConfirmModal.vue";
import AppEmptyState from "../../design-system/primitives/AppEmptyState.vue";
import AppErrorState from "../../design-system/primitives/AppErrorState.vue";
import AppLoadingState from "../../design-system/primitives/AppLoadingState.vue";
import AppStatusPill from "../../design-system/primitives/AppStatusPill.vue";
import DashboardPageShell from "../../design-system/patterns/DashboardPageShell.vue";
import PaddedSectionCard from "../../design-system/patterns/PaddedSectionCard.vue";

const route = useRoute();
const practitionerOps = usePractitionerOps();
const dealOps = useDealOps();
const payoutOps = usePayoutOps();
const moderation = useModerationCenter();
const selectedCount = ref(0);

const mode = computed(() => String(route.meta.adminMode || "generic"));
const query = computed({
  get: () => {
    if (mode.value === "practitioners") return practitionerOps.query.value;
    if (mode.value === "deals") return dealOps.query.value;
    if (mode.value === "payouts") return payoutOps.query.value;
    if (mode.value === "moderation") return moderation.query.value;
    return "";
  },
  set: (value: string) => {
    if (mode.value === "practitioners") practitionerOps.query.value = value;
    if (mode.value === "deals") dealOps.query.value = value;
    if (mode.value === "payouts") payoutOps.query.value = value;
    if (mode.value === "moderation") moderation.query.value = value;
  }
});

const sectionTitle = computed(() => String(route.meta.adminTitle || "Operations"));
const sectionEyebrow = computed(() => String(route.meta.adminEyebrow || "Admin"));
const sectionSubtitle = computed(() => String(route.meta.adminSubtitle || "Platform operation workspace"));
const practitionerColumns = [
  { key: "name", label: "Name" },
  { key: "subscription_status", label: "Subscription" },
  { key: "payout_status", label: "Payout" },
  { key: "stripe_state", label: "Stripe" },
  { key: "verification_state", label: "Verification" },
  { key: "health", label: "Health" },
  { key: "actions", label: "Actions" }
];
const dealColumns = [
  { key: "title", label: "Deal" },
  { key: "practitioner_name", label: "Practitioner" },
  { key: "status", label: "Status" },
  { key: "moderation_state", label: "Moderation" },
  { key: "revenue", label: "Revenue" },
  { key: "bookings_count", label: "Bookings" },
  { key: "actions", label: "Actions" }
];
const payoutColumns = [
  { key: "id", label: "ID" },
  { key: "creator", label: "Creator" },
  { key: "amount", label: "Amount" },
  { key: "status", label: "Status" },
  { key: "transfer_state", label: "Transfer" },
  { key: "actions", label: "Actions" }
];
const moderationColumns = [
  { key: "id", label: "ID" },
  { key: "entity", label: "Entity" },
  { key: "reason", label: "Reason" },
  { key: "severity", label: "Severity" },
  { key: "state", label: "State" },
  { key: "actions", label: "Actions" }
];

type PendingAction = { title: string; description: string; run: () => void | Promise<void> };
const pendingAction = ref<PendingAction | null>(null);
const confirmOpen = computed(() => Boolean(pendingAction.value));
const confirmTitle = computed(() => pendingAction.value?.title || "Confirm action");
const confirmDescription = computed(() => pendingAction.value?.description || "");
const currentError = computed(() => {
  if (mode.value === "practitioners") return practitionerOps.error.value;
  if (mode.value === "deals") return dealOps.error.value;
  if (mode.value === "payouts") return payoutOps.error.value;
  return "";
});
const currentLoading = computed(() => {
  if (mode.value === "practitioners") return practitionerOps.loading.value;
  if (mode.value === "deals") return dealOps.loading.value;
  if (mode.value === "payouts") return payoutOps.loading.value;
  return false;
});

const placeholders = computed(() => [
  { title: `${sectionTitle.value} Queue`, copy: "Operational queue and workflow actions." },
  { title: "Analytics", copy: "Trend and risk signals for this vertical." },
  { title: "Actions", copy: "Scoped controls and destructive safeguards." }
]);

async function refreshCurrent() {
  if (mode.value === "practitioners") return practitionerOps.load();
  if (mode.value === "deals") return dealOps.load();
  if (mode.value === "payouts") return payoutOps.load();
}

function confirmAction(title: string, description: string, run: () => void | Promise<void>) {
  pendingAction.value = { title, description, run };
}

function confirmBulkAction(title: string, description: string, run: () => void | Promise<void>) {
  confirmAction(title, description, run);
}

function handleSelectionChange(keys: string[]) {
  selectedCount.value = keys.length;
}

function closeConfirm() {
  pendingAction.value = null;
}

async function runConfirm() {
  if (!pendingAction.value) return;
  const toRun = pendingAction.value.run;
  pendingAction.value = null;
  await toRun();
}

async function bulkPractitionerAction(action: "impersonate" | "suspend", keys: string[]) {
  await Promise.all(keys.map((id) => practitionerOps.performAction(action, id)));
}

async function bulkDealAction(action: "archive" | "moderate", keys: string[]) {
  await Promise.all(keys.map((id) => dealOps.performAction(action, id)));
}

async function bulkPayoutAction(action: "retry" | "mark_paid", keys: string[]) {
  if (action === "retry") {
    await Promise.all(keys.map((id) => payoutOps.retryPayout(id)));
    return;
  }
  await Promise.all(keys.map((id) => payoutOps.markPaid(id)));
}

async function bulkModerationResolve(keys: string[]) {
  await Promise.all(keys.map((id) => moderation.resolve(id)));
}

watch(mode, () => {
  void refreshCurrent();
}, { immediate: true });
</script>

<style scoped>
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.section-head__title { display: grid; gap: 4px; }
.section-head h3 { margin: 0; font-size: 24px; }
.section-head p { margin: 0; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: rgba(255,255,255,.58); }
.query { min-height: 42px; border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,18,30,.62); color: #dbe5f3; padding: 0 12px; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.actions button { border-radius: 999px; border: 1px solid rgba(255,255,255,.2); background: rgba(255,255,255,.05); color: rgba(255,255,255,.84); padding: 4px 10px; }
.actions .danger { border-color: rgba(255,159,166,.35); color: #ffc0c5; background: rgba(255,159,166,.1); }
.placeholder-grid { display: grid; grid-template-columns: repeat(3, minmax(0,1fr)); gap: 12px; }
.placeholder-card { border-radius: 14px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 14px; display: grid; gap: 8px; }
.placeholder-card h4 { margin: 0; font-size: 18px; }
.placeholder-card p { margin: 0; color: rgba(255,255,255,.64); }
@media (max-width: 767px) {
  .actions .danger { display: none; }
}
@media (max-width: 1023px) {
  .placeholder-grid { grid-template-columns: 1fr; }
}
</style>
