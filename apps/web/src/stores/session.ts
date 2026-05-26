import { reactive } from "vue";
import { bootstrapPractitioner, fetchMe, type MePayload } from "../services/api";
import { watchAuth, type AuthSnapshot } from "../firebase/auth";

export type AuthState = "loading" | "authenticated" | "unauthenticated";

export const sessionState = reactive({
  user: null as AuthSnapshot["user"],
  token: null as string | null,
  me: null as MePayload | null,
  meLoaded: false,
  onboardingComplete: false,
  loading: false,
  ready: false,
  statusText: "",
  authState: "loading" as AuthState
});

export function clearSessionState(): void {
  sessionState.me = null;
  sessionState.user = null;
  sessionState.token = null;
  sessionState.meLoaded = false;
  sessionState.onboardingComplete = false;
  sessionState.statusText = "";
  sessionState.loading = false;
  sessionState.ready = true;
  sessionState.authState = "unauthenticated";
}

let started = false;
let sessionResolveQueue: Array<() => void> = [];

function resolveSessionWaiters(): void {
  const waiters = sessionResolveQueue;
  sessionResolveQueue = [];
  waiters.forEach((resolve) => resolve());
}

function setAuthLoading(): void {
  sessionState.loading = true;
  sessionState.authState = "loading";
}

function markUnauthenticated(): void {
  sessionState.authState = "unauthenticated";
}

function markAuthenticated(): void {
  sessionState.authState = "authenticated";
}

function finishAuthCycle(): void {
  sessionState.ready = true;
  sessionState.loading = false;
  resolveSessionWaiters();
}

export async function waitForSessionResolution(): Promise<void> {
  if (sessionState.ready && !sessionState.loading) return;
  await new Promise<void>((resolve) => {
    sessionResolveQueue.push(resolve);
  });
}

export function initSessionWatcher(): void {
  if (started) return;
  started = true;
  sessionState.ready = false;
  setAuthLoading();

  watchAuth(async (next) => {
    setAuthLoading();
    sessionState.user = next.user;
    sessionState.token = next.token;
    sessionState.me = null;
    sessionState.meLoaded = false;
    sessionState.onboardingComplete = false;

    if (next.token) {
      try {
        sessionState.me = await fetchMe(next.token);
        sessionState.meLoaded = true;
        sessionState.onboardingComplete = Boolean(sessionState.me?.practitioner_id);
        markAuthenticated();
      } catch (err) {
        sessionState.user = null;
        sessionState.token = null;
        sessionState.me = null;
        sessionState.meLoaded = false;
        sessionState.statusText = `Failed to load /me: ${String(err)}`;
        markUnauthenticated();
      }
    } else {
      markUnauthenticated();
    }
    finishAuthCycle();
  });
}

export async function refreshMe(): Promise<void> {
  if (!sessionState.token) return;
  setAuthLoading();
  try {
    sessionState.me = await fetchMe(sessionState.token);
    sessionState.meLoaded = true;
    sessionState.onboardingComplete = Boolean(sessionState.me?.practitioner_id);
    markAuthenticated();
  } catch (err) {
    clearSessionState();
    sessionState.statusText = `Failed to refresh /me: ${String(err)}`;
    markUnauthenticated();
  } finally {
    finishAuthCycle();
  }
}

export async function bootstrapMe(name?: string): Promise<void> {
  if (!sessionState.token) return;
  const nextName = name || sessionState.user?.displayName || "New Practitioner";
  await bootstrapPractitioner(sessionState.token, nextName);
  await refreshMe();
}
