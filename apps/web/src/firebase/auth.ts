import { initializeApp } from "firebase/app";
import {
  browserLocalPersistence,
  createUserWithEmailAndPassword,
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  setPersistence,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  updateProfile,
  type User
} from "firebase/auth";
import { firebaseConfig, hasFirebaseConfig } from "./config";

const app = hasFirebaseConfig ? initializeApp(firebaseConfig) : null;
const auth = app ? getAuth(app) : null;
const googleProvider = new GoogleAuthProvider();
if (auth) {
  void setPersistence(auth, browserLocalPersistence);
}

function requireAuth() {
  if (!hasFirebaseConfig) {
    throw new Error("Firebase config missing. Add VITE_FIREBASE_* values in apps/web/.env.local");
  }
  if (!auth) {
    throw new Error("Firebase auth failed to initialize.");
  }
  return auth;
}

export type AuthSnapshot = {
  user: User | null;
  token: string | null;
};

export function watchAuth(cb: (state: AuthSnapshot) => void): () => void {
  if (!hasFirebaseConfig || !auth) {
    cb({ user: null, token: null });
    return () => undefined;
  }

  return onAuthStateChanged(auth, async (user) => {
    try {
      const token = user ? await user.getIdToken() : null;
      cb({ user, token });
    } catch (err) {
      console.warn("[web] Firebase token refresh failed", err);
      cb({ user: null, token: null });
    }
  });
}

export async function loginWithGoogle(): Promise<void> {
  const currentAuth = requireAuth();
  await signInWithPopup(currentAuth, googleProvider);
}

export async function loginWithEmail(email: string, password: string): Promise<void> {
  const currentAuth = requireAuth();
  await signInWithEmailAndPassword(currentAuth, email, password);
}

export async function signupWithEmail(name: string, email: string, password: string): Promise<void> {
  const currentAuth = requireAuth();
  const result = await createUserWithEmailAndPassword(currentAuth, email, password);
  if (name.trim()) {
    await updateProfile(result.user, { displayName: name.trim() });
  }
}

export async function updateCurrentUserProfile(displayName: string, photoURL?: string | null): Promise<void> {
  const currentAuth = requireAuth();
  if (!currentAuth.currentUser) return;
  await updateProfile(currentAuth.currentUser, {
    displayName: displayName.trim() || currentAuth.currentUser.displayName || "",
    photoURL: photoURL?.trim() || null
  });
}

export async function logout(): Promise<void> {
  const currentAuth = requireAuth();
  await signOut(currentAuth);
}

export async function getFreshIdToken(forceRefresh = false): Promise<string> {
  const currentAuth = requireAuth();
  if (!currentAuth.currentUser) {
    throw new Error("Authentication session expired.");
  }
  return currentAuth.currentUser.getIdToken(forceRefresh);
}
