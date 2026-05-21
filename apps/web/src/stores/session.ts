import { reactive } from "vue";
import { bootstrapPractitioner, fetchMe, type MePayload } from "../services/api";
import { watchAuth, type AuthSnapshot } from "../firebase/auth";

export const sessionState = reactive({
  user: null as AuthSnapshot["user"],
  token: null as string | null,
  me: null as MePayload | null,
  ready: false,
  statusText: ""
});

let started = false;

export function initSessionWatcher(): void {
  if (started) return;
  started = true;

  watchAuth(async (next) => {
    sessionState.user = next.user;
    sessionState.token = next.token;
    sessionState.me = null;

    if (next.token) {
      try {
        sessionState.me = await fetchMe(next.token);
      } catch (err) {
        sessionState.statusText = `Failed to load /me: ${String(err)}`;
      }
    }
    sessionState.ready = true;
  });
}

export async function refreshMe(): Promise<void> {
  if (!sessionState.token) return;
  sessionState.me = await fetchMe(sessionState.token);
}

export async function bootstrapMe(): Promise<void> {
  if (!sessionState.token) return;
  const name = sessionState.user?.displayName || "New Practitioner";
  await bootstrapPractitioner(sessionState.token, name);
  await refreshMe();
}
