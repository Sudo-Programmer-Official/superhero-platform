import { reactive } from "vue";
import { bootstrapPractitioner, fetchMe, type MePayload } from "../services/api";
import { watchAuth, type AuthSnapshot } from "../firebase/auth";

export const sessionState = reactive({
  user: null as AuthSnapshot["user"],
  token: null as string | null,
  me: null as MePayload | null,
  onboardingComplete: false,
  loading: false,
  ready: false,
  statusText: ""
});

let started = false;

export function initSessionWatcher(): void {
  if (started) return;
  started = true;

  watchAuth(async (next) => {
    sessionState.loading = true;
    sessionState.user = next.user;
    sessionState.token = next.token;
    sessionState.me = null;
    sessionState.onboardingComplete = false;

    if (next.token) {
      try {
        sessionState.me = await fetchMe(next.token);
        sessionState.onboardingComplete = Boolean(sessionState.me?.practitioner_id);
      } catch (err) {
        sessionState.statusText = `Failed to load /me: ${String(err)}`;
      }
    }
    sessionState.ready = true;
    sessionState.loading = false;
  });
}

export async function refreshMe(): Promise<void> {
  if (!sessionState.token) return;
  sessionState.loading = true;
  sessionState.me = await fetchMe(sessionState.token);
  sessionState.onboardingComplete = Boolean(sessionState.me?.practitioner_id);
  sessionState.loading = false;
}

export async function bootstrapMe(name?: string): Promise<void> {
  if (!sessionState.token) return;
  const nextName = name || sessionState.user?.displayName || "New Practitioner";
  await bootstrapPractitioner(sessionState.token, nextName);
  await refreshMe();
}
