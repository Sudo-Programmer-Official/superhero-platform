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
        <select
          v-if="mode === 'redemptions'"
          v-model="redemptionOps.window"
          class="window-select"
          @change="onRedemptionWindowChange"
        >
          <option value="24h">Last 24h</option>
          <option value="7d">Last 7d</option>
          <option value="30d">Last 30d</option>
          <option value="all">All time</option>
        </select>
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

      <template v-else-if="mode === 'bookings'">
        <AppDataTable
          :columns="bookingColumns"
          :rows="bookingOps.filtered"
          :row-key="(row) => String(row.id)"
          selectable
          @selection-change="handleSelectionChange"
        >
          <template #cell-total_amount="{ row }">${{ Number(row.total_amount).toFixed(2) }} {{ row.currency }}</template>
          <template #cell-payment_status="{ row }"><AppStatusPill :status="String(row.payment_status)" /></template>
          <template #cell-redemption_status="{ row }"><AppStatusPill :status="String(row.redemption_status)" /></template>
          <template #cell-actions="{ row }">
            <div class="actions">
              <button @click="openTimeline('booking', String(row.id), row.booking_number)">Timeline</button>
              <button v-if="row.wallet_pass_id" @click="openWalletPassContext(String(row.wallet_pass_id))">Open pass</button>
              <button @click="openDealContext(String(row.deal_title))">Open deal</button>
              <button @click="openPractitionerContext(String(row.practitioner_name))">Open practitioner</button>
            </div>
          </template>
          <template #empty><AppEmptyState title="No bookings" description="No bookings found in the current scope." /></template>
        </AppDataTable>
      </template>

      <template v-else-if="mode === 'wallet-passes'">
        <AppDataTable
          :columns="walletPassColumns"
          :rows="walletPassOps.filtered"
          :row-key="(row) => String(row.id)"
          selectable
          @selection-change="handleSelectionChange"
        >
          <template #cell-id="{ row }">#{{ String(row.id).slice(0, 8) }}</template>
          <template #cell-pass_status="{ row }"><AppStatusPill :status="String(row.pass_status)" /></template>
          <template #cell-redemption_status="{ row }"><AppStatusPill :status="String(row.redemption_status)" /></template>
          <template #cell-actions="{ row }">
            <div class="actions">
              <button @click="openTimeline('wallet_pass', String(row.id), `Pass ${String(row.id).slice(0, 8)}`)">Timeline</button>
              <button @click="openRedemptionContext(String(row.id))">Open redemptions</button>
              <button @click="openDealContext(String(row.deal_title))">Open deal</button>
            </div>
          </template>
          <template #empty><AppEmptyState title="No wallet passes" description="No wallet pass lifecycle records found." /></template>
        </AppDataTable>
      </template>

      <template v-else-if="mode === 'redemptions'">
        <AppDataTable
          :columns="redemptionColumns"
          :rows="redemptionOps.filtered"
          :row-key="(row) => String(row.wallet_pass_id)"
          selectable
          @selection-change="handleSelectionChange"
        >
          <template #cell-wallet_pass_id="{ row }">#{{ String(row.wallet_pass_id).slice(0, 8) }}</template>
          <template #cell-risk_level="{ row }"><AppStatusPill :status="String(row.risk_level)" /></template>
          <template #cell-actions="{ row }">
            <div class="actions">
              <button @click="openTimeline('redemption', String(row.wallet_pass_id), `Redemption ${String(row.wallet_pass_id).slice(0, 8)}`)">Timeline</button>
              <button @click="openWalletPassContext(String(row.wallet_pass_id))">Open pass</button>
            </div>
          </template>
          <template #empty><AppEmptyState title="No redemption events" description="No redemption lifecycle events found." /></template>
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

    <AppModal :open="timelineOpen" @close="closeTimeline">
      <div class="timeline-modal">
        <div class="timeline-head">
          <h4>{{ timelineTitle }}</h4>
          <button class="timeline-refresh" @click="reloadTimeline">Refresh</button>
        </div>
        <p class="timeline-sub">{{ timelineEntityType }} · {{ timelineEntityId }}</p>
        <p v-if="timelineError" class="timeline-error">{{ timelineError }}</p>
        <p v-else-if="timelineLoading" class="timeline-loading">Loading timeline…</p>
        <div v-else-if="timelineEvents.length === 0" class="timeline-empty">No timeline events yet.</div>
        <ul v-else class="timeline-list">
          <li v-for="event in timelineEvents" :key="event.id" class="timeline-item">
            <p class="timeline-event">{{ event.event_type }}</p>
            <p class="timeline-time">{{ formatTimelineTime(event.created_at) }}</p>
            <p class="timeline-entity">{{ event.entity_type }} · {{ event.entity_id }}</p>
            <div v-if="timelineMetadataPairs(event).length" class="timeline-meta">
              <span v-for="pair in timelineMetadataPairs(event)" :key="`${event.id}-${pair.key}`" class="meta-chip">
                {{ pair.key }}: {{ pair.value }}
              </span>
            </div>
          </li>
        </ul>
      </div>
    </AppModal>
  </DashboardPageShell>
</template>

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import { useDealOps } from "../composables/useDealOps";
import { useModerationCenter } from "../composables/useModerationCenter";
import { usePayoutOps } from "../composables/usePayoutOps";
import { usePractitionerOps } from "../composables/usePractitionerOps";
import { useBookingOps } from "../composables/useBookingOps";
import { useRedemptionOps } from "../composables/useRedemptionOps";
import { useWalletPassOps } from "../composables/useWalletPassOps";
import { listAdminTimeline, type AdminTimelineEventRow } from "../../services/api";
import { sessionState } from "../../stores/session";
import AppDataTable from "../../design-system/patterns/AppDataTable.vue";
import AppButton from "../../design-system/primitives/AppButton.vue";
import AppConfirmModal from "../../design-system/primitives/AppConfirmModal.vue";
import AppEmptyState from "../../design-system/primitives/AppEmptyState.vue";
import AppErrorState from "../../design-system/primitives/AppErrorState.vue";
import AppLoadingState from "../../design-system/primitives/AppLoadingState.vue";
import AppModal from "../../design-system/primitives/AppModal.vue";
import AppStatusPill from "../../design-system/primitives/AppStatusPill.vue";
import DashboardPageShell from "../../design-system/patterns/DashboardPageShell.vue";
import PaddedSectionCard from "../../design-system/patterns/PaddedSectionCard.vue";

const route = useRoute();
const router = useRouter();
const practitionerOps = usePractitionerOps();
const dealOps = useDealOps();
const payoutOps = usePayoutOps();
const moderation = useModerationCenter();
const bookingOps = useBookingOps();
const walletPassOps = useWalletPassOps();
const redemptionOps = useRedemptionOps();
const selectedCount = ref(0);
const timelineOpen = ref(false);
const timelineLoading = ref(false);
const timelineError = ref("");
const timelineEvents = ref<AdminTimelineEventRow[]>([]);
const timelineEntityType = ref("");
const timelineEntityId = ref("");
const timelineTitle = ref("Timeline");

const mode = computed(() => String(route.meta.adminMode || "generic"));
const query = computed({
  get: () => {
    if (mode.value === "practitioners") return practitionerOps.query.value;
    if (mode.value === "deals") return dealOps.query.value;
    if (mode.value === "payouts") return payoutOps.query.value;
    if (mode.value === "bookings") return bookingOps.query.value;
    if (mode.value === "wallet-passes") return walletPassOps.query.value;
    if (mode.value === "redemptions") return redemptionOps.query.value;
    if (mode.value === "moderation") return moderation.query.value;
    return "";
  },
  set: (value: string) => {
    if (mode.value === "practitioners") practitionerOps.query.value = value;
    if (mode.value === "deals") dealOps.query.value = value;
    if (mode.value === "payouts") payoutOps.query.value = value;
    if (mode.value === "bookings") bookingOps.query.value = value;
    if (mode.value === "wallet-passes") walletPassOps.query.value = value;
    if (mode.value === "redemptions") redemptionOps.query.value = value;
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
const bookingColumns = [
  { key: "booking_number", label: "Booking" },
  { key: "deal_title", label: "Deal" },
  { key: "practitioner_name", label: "Practitioner" },
  { key: "customer_email", label: "Attendee" },
  { key: "total_amount", label: "Amount" },
  { key: "payment_status", label: "Payment" },
  { key: "redemption_status", label: "Redemption" },
  { key: "actions", label: "Actions" }
];
const walletPassColumns = [
  { key: "id", label: "Pass ID" },
  { key: "deal_title", label: "Deal" },
  { key: "practitioner_name", label: "Practitioner" },
  { key: "attendee_email", label: "Attendee" },
  { key: "pass_status", label: "Pass" },
  { key: "redemption_status", label: "Redemption" },
  { key: "wallet_type", label: "Wallet" },
  { key: "actions", label: "Actions" }
];
const redemptionColumns = [
  { key: "wallet_pass_id", label: "Pass" },
  { key: "deal_title", label: "Deal" },
  { key: "practitioner_name", label: "Practitioner" },
  { key: "attendee_email", label: "Attendee" },
  { key: "duplicate_attempts", label: "Duplicates" },
  { key: "invalid_attempts", label: "Invalid" },
  { key: "risk_level", label: "Risk" },
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
  if (mode.value === "bookings") return bookingOps.error.value;
  if (mode.value === "wallet-passes") return walletPassOps.error.value;
  if (mode.value === "redemptions") return redemptionOps.error.value;
  return "";
});
const currentLoading = computed(() => {
  if (mode.value === "practitioners") return practitionerOps.loading.value;
  if (mode.value === "deals") return dealOps.loading.value;
  if (mode.value === "payouts") return payoutOps.loading.value;
  if (mode.value === "bookings") return bookingOps.loading.value;
  if (mode.value === "wallet-passes") return walletPassOps.loading.value;
  if (mode.value === "redemptions") return redemptionOps.loading.value;
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
  if (mode.value === "bookings") return bookingOps.load();
  if (mode.value === "wallet-passes") return walletPassOps.load();
  if (mode.value === "redemptions") return redemptionOps.load();
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

function onRedemptionWindowChange() {
  if (mode.value === "redemptions") {
    void redemptionOps.load();
  }
}

async function navigateAdmin(name: string, queryText = "") {
  if (name === "admin-bookings") bookingOps.query.value = queryText;
  if (name === "admin-wallet-passes") walletPassOps.query.value = queryText;
  if (name === "admin-redemptions") redemptionOps.query.value = queryText;
  if (name === "admin-deals") dealOps.query.value = queryText;
  if (name === "admin-practitioners") practitionerOps.query.value = queryText;
  await router.push({ name });
}

async function openWalletPassContext(walletPassId: string) {
  await navigateAdmin("admin-wallet-passes", walletPassId);
}

async function openRedemptionContext(walletPassId: string) {
  await navigateAdmin("admin-redemptions", walletPassId);
}

async function openDealContext(dealTitle: string) {
  await navigateAdmin("admin-deals", dealTitle);
}

async function openPractitionerContext(practitionerName: string) {
  await navigateAdmin("admin-practitioners", practitionerName);
}

async function openTimeline(entityType: string, entityId: string, title: string) {
  timelineEntityType.value = entityType;
  timelineEntityId.value = entityId;
  timelineTitle.value = title;
  timelineOpen.value = true;
  await reloadTimeline();
}

async function reloadTimeline() {
  if (!sessionState.token || !timelineEntityType.value || !timelineEntityId.value) return;
  timelineLoading.value = true;
  timelineError.value = "";
  try {
    timelineEvents.value = await listAdminTimeline(
      sessionState.token,
      timelineEntityType.value,
      timelineEntityId.value,
      100
    );
  } catch (err) {
    timelineError.value = `Failed to load timeline: ${String(err)}`;
  } finally {
    timelineLoading.value = false;
  }
}

function closeTimeline() {
  timelineOpen.value = false;
  timelineEvents.value = [];
  timelineError.value = "";
}

function formatTimelineTime(value: string): string {
  return new Date(value).toLocaleString();
}

function timelineMetadataPairs(event: AdminTimelineEventRow): Array<{ key: string; value: string }> {
  const md = event.metadata || {};
  const priorityKeys = [
    "reason",
    "booking_number",
    "amount",
    "currency",
    "quantity",
    "deal_id",
    "customer_id",
    "wallet_pass_id",
  ];
  const pairs: Array<{ key: string; value: string }> = [];
  for (const key of priorityKeys) {
    const raw = md[key];
    if (raw === undefined || raw === null || raw === "") continue;
    pairs.push({ key, value: String(raw) });
  }
  return pairs;
}
</script>

<style scoped>
.section-head { display: flex; justify-content: space-between; align-items: center; gap: 12px; }
.section-head__title { display: grid; gap: 4px; }
.section-head h3 { margin: 0; font-size: 24px; }
.section-head p { margin: 0; font-size: 11px; letter-spacing: .08em; text-transform: uppercase; color: rgba(255,255,255,.58); }
.query { min-height: 42px; border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,18,30,.62); color: #dbe5f3; padding: 0 12px; }
.window-select { min-height: 42px; border-radius: 10px; border: 1px solid rgba(255,255,255,.14); background: rgba(12,18,30,.62); color: #dbe5f3; padding: 0 12px; }
.actions { display: flex; gap: 8px; flex-wrap: wrap; }
.actions button { border-radius: 999px; border: 1px solid rgba(255,255,255,.2); background: rgba(255,255,255,.05); color: rgba(255,255,255,.84); padding: 4px 10px; }
.actions .danger { border-color: rgba(255,159,166,.35); color: #ffc0c5; background: rgba(255,159,166,.1); }
.timeline-modal { display: grid; gap: 10px; }
.timeline-head { display: flex; align-items: center; justify-content: space-between; gap: 10px; }
.timeline-head h4 { margin: 0; font-size: 20px; }
.timeline-refresh { border-radius: 10px; border: 1px solid rgba(255,255,255,.16); background: rgba(255,255,255,.05); color: rgba(255,255,255,.86); padding: 6px 10px; }
.timeline-sub { margin: 0; color: rgba(255,255,255,.65); font-size: 12px; }
.timeline-error { margin: 0; color: #ffbcbc; }
.timeline-loading, .timeline-empty { margin: 0; color: rgba(255,255,255,.74); }
.timeline-list { list-style: none; margin: 0; padding: 0; display: grid; gap: 8px; max-height: 420px; overflow: auto; }
.timeline-item { border-radius: 10px; border: 1px solid rgba(255,255,255,.1); background: rgba(255,255,255,.03); padding: 8px 10px; display: grid; gap: 2px; }
.timeline-event { margin: 0; font-weight: 600; }
.timeline-time, .timeline-entity { margin: 0; font-size: 12px; color: rgba(255,255,255,.68); }
.timeline-meta { margin-top: 6px; display: flex; flex-wrap: wrap; gap: 6px; }
.meta-chip { border: 1px solid rgba(255,255,255,.16); border-radius: 999px; padding: 3px 8px; font-size: 11px; color: rgba(255,255,255,.82); background: rgba(255,255,255,.05); }
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
