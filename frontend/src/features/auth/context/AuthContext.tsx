import type { Session, User } from "@supabase/supabase-js";
import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { supabase } from "../../../lib/supabase";
import type { UserRole } from "../types/auth";

type AuthContextValue = {
  session: Session | null;
  user: User | null;
  role: UserRole | null;
  roleLoading: boolean;
  loading: boolean;
  signOut: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(true);
  const [role, setRole] = useState<UserRole | null>(null);
  const [roleLoading, setRoleLoading] = useState(true);

  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setLoading(false);
    });

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((_event, currentSession) => {
      setSession(currentSession);
      setLoading(false);
    });

    return () => subscription.unsubscribe();
  }, []);

  useEffect(() => {
    const userId = session?.user?.id;

    if (!userId) {
      setRole(null);
      setRoleLoading(false);
      return;
    }

    let cancelled = false;
    setRoleLoading(true);

    // maybeSingle, not single: a user who has signed up but not yet
    // finished onboarding has no profiles row yet - that's a normal
    // transient state (role stays null), not an error.
    supabase
      .from("profiles")
      .select("role")
      .eq("id", userId)
      .maybeSingle()
      .then(({ data }) => {
        if (!cancelled) {
          setRole((data?.role as UserRole | undefined) ?? null);
          setRoleLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [session?.user?.id]);

  const value = useMemo(
    () => ({
      session,
      user: session?.user ?? null,
      role,
      roleLoading,
      loading,
      signOut: async () => {
        await supabase.auth.signOut();
      },
    }),
    [session, loading, role, roleLoading],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider");
  }

  return context;
}
