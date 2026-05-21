import { initializeApp } from "firebase/app";
import {
  GoogleAuthProvider,
  getAuth,
  onAuthStateChanged,
  signInWithEmailAndPassword,
  signInWithPopup,
  signOut,
  type User
} from "firebase/auth";
import { firebaseConfig, hasFirebaseConfig } from "./config";

const app = hasFirebaseConfig ? initializeApp(firebaseConfig) : null;
const auth = app ? getAuth(app) : null;
const googleProvider = new GoogleAuthProvider();

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

export async function logout(): Promise<void> {
  if (!auth) return;
  await signOut(auth);
}
