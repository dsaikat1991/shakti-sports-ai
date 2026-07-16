import { useQuery } from "@tanstack/react-query";
import { LogOut, User } from "lucide-react";
import { useState } from "react";
import { Link } from "react-router-dom";
import { roleHomeRoute } from "../../constants/routes";
import { useAuth } from "../../features/auth/context/AuthContext";
import { useAvatarSignedUrl } from "../../features/athlete/hooks/useAvatarUpload";
import { supabase } from "../../lib/supabase";

// Deliberately not features/athlete/hooks/useAthleteProfile - that hook
// also queries athlete_profiles, which coach/academy accounts have no
// row in. This menu is shared by every role, so it only ever asks for
// the one column (profiles.avatar_url) every role actually has.
function useOwnAvatarPath(userId?: string) {
  return useQuery({
    queryKey: ["own-avatar-path", userId],
    queryFn: async () => {
      if (!userId) return null;
      const { data } = await supabase
        .from("profiles")
        .select("avatar_url")
        .eq("id", userId)
        .maybeSingle();
      return data?.avatar_url ?? null;
    },
    enabled: Boolean(userId),
  });
}

export default function UserMenu() {
  const { user, role, signOut } = useAuth();
  const [open, setOpen] = useState(false);

  const email = user?.email ?? "";
  const initial = email.charAt(0).toUpperCase() || "U";

  const { data: avatarPath } = useOwnAvatarPath(user?.id);
  const { data: avatarUrl } = useAvatarSignedUrl(avatarPath);

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        className="flex cursor-pointer items-center gap-3 rounded-xl border border-gray-200 bg-white px-3 py-2 transition hover:border-[#F0600E]"
      >
        <div className="flex h-9 w-9 items-center justify-center overflow-hidden rounded-full bg-[#F0600E] text-sm font-black text-white">
          {avatarUrl ? (
            <img src={avatarUrl} alt="" className="h-full w-full object-cover" />
          ) : (
            initial
          )}
        </div>

        <span className="hidden max-w-36 truncate text-sm font-bold text-gray-800 sm:block">
          {email}
        </span>
      </button>

      {open && (
        <div className="absolute right-0 mt-3 w-64 overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-2xl shadow-gray-200">
          <div className="border-b border-gray-100 p-4">
            <p className="text-sm font-bold text-gray-950">Signed in</p>
            <p className="mt-1 truncate text-xs text-gray-500">{email}</p>
          </div>

          <div className="p-2">
            <Link
              to={roleHomeRoute(role)}
              onClick={() => setOpen(false)}
              className="flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-semibold text-gray-700 hover:bg-orange-50 hover:text-[#F0600E]"
            >
              <User className="h-4 w-4" />
              Dashboard
            </Link>

            <button
              type="button"
              onClick={signOut}
              className="flex w-full cursor-pointer items-center gap-3 rounded-xl px-3 py-2 text-left text-sm font-semibold text-gray-700 hover:bg-red-50 hover:text-red-600"
            >
              <LogOut className="h-4 w-4" />
              Sign Out
            </button>
          </div>
        </div>
      )}
    </div>
  );
}