import { computed, reactive } from "vue";
import { normalizeAdminRole, type AdminRole } from "../domain/permissions";
import { sessionState } from "../../stores/session";

export const adminState = reactive({
  tenant: "default",
  alerts: [] as string[]
});

export const currentAdminRole = computed<AdminRole>(() => normalizeAdminRole(sessionState.me?.role || "operator"));
