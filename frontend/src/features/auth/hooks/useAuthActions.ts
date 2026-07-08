import * as auth from "../services/auth.service";

export function useAuthActions() {
  return {
    signIn: auth.signIn,
    signUp: auth.signUp,
    signInWithGoogle: auth.signInWithGoogle,
    signOut: auth.signOut,
  };
}