import { Bookmark, Loader2, ShieldOff, Trash2 } from "lucide-react";

import { useAuth } from "../../auth/context/AuthContext";
import { useBookmarkedAthletes, useRemoveBookmark } from "../hooks/useBookmarks";
import { useRequestConnectionByAthleteId } from "../hooks/useDiscoverySearch";

export default function PartnerBookmarks() {
  const { user } = useAuth();
  const { data: bookmarks = [], isLoading, error } = useBookmarkedAthletes(Boolean(user?.id));
  const removeBookmark = useRemoveBookmark();
  const requestConnection = useRequestConnectionByAthleteId();

  return (
    <div className="mx-auto max-w-6xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-[#F0600E]">
        Scouting
      </p>
      <h1 className="mt-3 font-['Anton'] text-5xl uppercase leading-none text-gray-950 md:text-6xl">
        Bookmarks
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-gray-600">
        Athletes you've bookmarked from Discover, before sending a connection
        request. A bookmark grants no extra access - it's just a private
        reminder for you.
      </p>

      {isLoading && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-gray-200 bg-white p-6 text-sm font-semibold text-gray-600 shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-[#F0600E]" />
          Loading your bookmarks...
        </div>
      )}

      {error && (
        <div className="mt-10 rounded-3xl border border-red-200 bg-red-50 p-6 text-sm font-semibold text-red-700">
          {error.message}
        </div>
      )}

      {!isLoading && !error && bookmarks.length === 0 && (
        <div className="mt-10 rounded-4xl border border-dashed border-gray-300 bg-gray-50 p-10 text-center">
          <Bookmark className="mx-auto h-11 w-11 text-gray-400" />
          <h2 className="mt-5 text-2xl font-bold text-gray-950">No bookmarks yet</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-gray-500">
            Bookmark an athlete from Discover to keep track of them here.
          </p>
        </div>
      )}

      {!isLoading && bookmarks.length > 0 && (
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {bookmarks.map((bookmark) => (
            <div
              key={bookmark.bookmark_id}
              className="rounded-4xl border border-gray-200 bg-white p-6 shadow-sm"
            >
              {bookmark.visible ? (
                <>
                  <h2 className="text-xl font-bold text-gray-950">{bookmark.full_name}</h2>
                  <p className="mt-2 text-sm text-gray-500">
                    {bookmark.preferred_event ?? "Event not set"}
                    {bookmark.secondary_event ? ` · ${bookmark.secondary_event}` : ""}
                    {bookmark.state ? ` · ${bookmark.state}` : ""}
                  </p>

                  <div className="mt-5 flex items-center gap-3">
                    <button
                      type="button"
                      onClick={() => requestConnection.mutate(bookmark.athlete_id)}
                      disabled={requestConnection.isPending}
                      className="inline-flex items-center gap-2 rounded-xl bg-[#F0600E] px-4 py-2.5 text-sm font-bold text-white transition hover:bg-orange-700 disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Request to Connect
                    </button>

                    <button
                      type="button"
                      onClick={() => removeBookmark.mutate(bookmark.bookmark_id)}
                      disabled={removeBookmark.isPending}
                      className="inline-flex items-center gap-2 rounded-xl border border-gray-200 px-4 py-2.5 text-sm font-bold text-gray-600 transition hover:border-red-300 hover:text-red-600 disabled:opacity-50"
                    >
                      <Trash2 className="h-4 w-4" />
                      Remove
                    </button>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-2 text-gray-400">
                    <ShieldOff className="h-5 w-5" />
                    <h2 className="text-lg font-bold">Athlete no longer discoverable</h2>
                  </div>
                  <p className="mt-2 text-sm leading-6 text-gray-500">
                    This athlete has withdrawn from discovery, or you're no
                    longer connected. Nothing about them is shown here
                    anymore.
                  </p>

                  <button
                    type="button"
                    onClick={() => removeBookmark.mutate(bookmark.bookmark_id)}
                    disabled={removeBookmark.isPending}
                    className="mt-5 inline-flex items-center gap-2 rounded-xl border border-gray-200 px-4 py-2.5 text-sm font-bold text-gray-600 transition hover:border-red-300 hover:text-red-600 disabled:opacity-50"
                  >
                    <Trash2 className="h-4 w-4" />
                    Remove bookmark
                  </button>
                </>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
