import { computed, ref } from "vue";
import { adminPractitionerAction, listAdminPractitioners, type AdminPractitionerRow } from "../../services/api";
import { sessionState } from "../../stores/session";
import { showToast } from "../../stores/toast";

export type PractitionerOpsRecord = {
  id: string;
  name: string;
  slug: string;
  subscription_status: "trial" | "active" | "grace" | "churn_risk";
  payout_status: "connected" | "restricted" | "pending";
  stripe_state: "connected" | "onboarding" | "missing";
  verification_state: "verified" | "pending" | "flagged";
  health: "healthy" | "watch" | "critical";
};

function mapRow(row: AdminPractitionerRow): PractitionerOpsRecord {
  return {
    id: row.id,
    name: row.name,
    slug: row.slug,
    subscription_status: (["trial", "active", "grace", "churn_risk"].includes(row.subscription_status) ? row.subscription_status : "active") as PractitionerOpsRecord["subscription_status"],
    payout_status: (["connected", "restricted", "pending"].includes(row.payout_status) ? row.payout_status : "pending") as PractitionerOpsRecord["payout_status"],
    stripe_state: (["connected", "onboarding", "missing"].includes(row.stripe_state) ? row.stripe_state : "missing") as PractitionerOpsRecord["stripe_state"],
    verification_state: (["verified", "pending", "flagged"].includes(row.verification_state) ? row.verification_state : "pending") as PractitionerOpsRecord["verification_state"],
    health: (["healthy", "watch", "critical"].includes(row.health) ? row.health : "watch") as PractitionerOpsRecord["health"]
  };
}

export function usePractitionerOps() {
  const loading = ref(true);
  const error = ref("");
  const query = ref("");
  const rows = ref<PractitionerOpsRecord[]>([]);

  const filtered = computed(() => {
    const q = query.value.trim().toLowerCase();
    if (!q) return rows.value;
    return rows.value.filter((row) => row.name.toLowerCase().includes(q) || row.slug.toLowerCase().includes(q));
  });

  async function load() {
    if (!sessionState.token) return;
    loading.value = true;
    error.value = "";
    try {
      const payload = await listAdminPractitioners(sessionState.token, query.value);
      console.debug("admin.practitioners.response", {
        isArray: Array.isArray(payload),
        type: Array.isArray(payload) ? "array" : typeof payload,
        length: Array.isArray(payload) ? payload.length : null
      });
      rows.value = Array.isArray(payload) ? payload.map(mapRow) : [];
    } catch (err) {
      error.value = `Failed practitioner ops: ${String(err)}`;
      showToast(error.value, "error");
    } finally {
      loading.value = false;
    }
  }

  async function performAction(action: "impersonate" | "suspend" | "activate" | "grant_credits" | "reset_onboarding" | "resend_verification", id: string) {
    if (!sessionState.token) return;
    try {
      const updated = await adminPractitionerAction(sessionState.token, id, action);
      const ix = rows.value.findIndex((row) => row.id === id);
      if (ix >= 0) rows.value[ix] = mapRow(updated);
      showToast(`Practitioner action applied: ${action.replace("_", " ")}`, "success");
    } catch (err) {
      showToast(`Practitioner action failed: ${String(err)}`, "error");
    }
  }

  return { error, filtered, load, loading, performAction, query, rows };
}
