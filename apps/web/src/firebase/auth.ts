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

export type AuthSnapshot = {
  user: User | null;
  token: string | null;
};

export function watchAuth(cb: (state: AuthSnapshot) => void): () => void {
  if (!auth) {
    cb({ user: null, token: null });
    return () => undefined;
  }

  return onAuthStateChanged(auth, async (user) => {
    const token = user ? await user.getIdToken() : null;
    cb({ user, token });
  });
}

export async function loginWithGoogle(): Promise<void> {
  if (!auth) return;
  await signInWithPopup(auth, googleProvider);
}

export async function loginWithEmail(email: string, password: string): Promise<void> {
  if (!auth) return;
  await signInWithEmailAndPassword(auth, email, password);
}

export async function signupWithEmail(name: string, email: string, password: string): Promise<void> {
  if (!auth) return;
  const result = await createUserWithEmailAndPassword(auth, email, password);
  if (name.trim()) {
    await updateProfile(result.user, { displayName: name.trim() });
  }
}

export async function updateCurrentUserProfile(displayName: string, photoURL?: string | null): Promise<void> {
  if (!auth?.currentUser) return;
  await updateProfile(auth.currentUser, {
    displayName: displayName.trim() || auth.currentUser.displayName || "",
    photoURL: photoURL?.trim() || null
  });
}

export async function logout(): Promise<void> {
  if (!auth) return;
  await signOut(auth);
}
