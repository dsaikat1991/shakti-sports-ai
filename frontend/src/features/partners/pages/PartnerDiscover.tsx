import { AlertCircle, ArrowRight, Bookmark, Loader2, Search } from "lucide-react";
import { useState } from "react";

import { useAuth } from "../../auth/context/AuthContext";
import { useBookmarkedAthletes, useCreateBookmark } from "../hooks/useBookmarks";
import {
  type DiscoverySearchFilters,
  useDiscoverySearch,
  useRequestConnectionByAthleteId,
} from "../hooks/useDiscoverySearch";

const EVENT_OPTIONS = ["Sprint", "Hurdles", "Long Jump", "High Jump"];

export default function PartnerDiscover() {
  const { user, role } = useAuth();
  const isAcademy = role === "academy";

  const [event, setEvent] = useState<string>("");
  const [state, setState] = useState<string>("");
  const [searched, setSearched] = useState(false);

  const filters: DiscoverySearchFilters = {
    event: event || null,
    state: state.trim() || null,
  };

  const { data: results = [], isLoading, error, isFetching } = useDiscoverySearch(filters);
  const { data: bookmarks = [] } = useBookmarkedAthletes(Boolean(user?.id));
  const createBookmark = useCreateBookmark(user?.id);
  const requestConnection = useRequestConnectionByAthleteId();

  const [sentTo, setSentTo] = useState<Record<string, string>>({});
  const bookmarkedIds = new Set(bookmarks.map((b) => b.athlete_id));

  function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    setSearched(true);
  }

  function handleConnect(athleteId: string, name: string) {
    requestConnection.mutate(athleteId, {
      onSuccess: () => setSentTo((prev) => ({ ...prev, [athleteId]: name })),
    });
  }

  return (
    <div className="mx-auto max-w-6xl">
      <p className="font-['JetBrains_Mono'] text-xs font-semibold uppercase tracking-[0.2em] text-brand-action">
        Discover
      </p>
      <h1 className="mt-3 text-2xl font-bold text-text-primary md:text-3xl">
        Find Athletes
      </h1>
      <p className="mt-4 max-w-2xl text-base leading-7 text-text-secondary">
        Search athletes who have chosen to be discoverable. Only name, event,
        and state are ever shown here - a connection request is required
        before anything else becomes visible.
      </p>

      <form
        onSubmit={handleSearch}
        className="mt-8 flex flex-col gap-3 rounded-3xl border border-border-default bg-surface-card p-4 shadow-sm sm:flex-row sm:items-center"
      >
        <select
          value={event}
          onChange={(e) => setEvent(e.target.value)}
          className="rounded-xl border border-border-default px-3 py-2.5 text-sm outline-none focus:border-brand-action"
        >
          <option value="">Any event</option>
          {EVENT_OPTIONS.map((opt) => (
            <option key={opt} value={opt}>
              {opt}
            </option>
          ))}
        </select>

        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-text-disabled" />
          <input
            value={state}
            onChange={(e) => setState(e.target.value)}
            placeholder="State (e.g. Maharashtra)"
            className="w-full rounded-xl border border-border-default py-2.5 pl-11 pr-4 text-sm outline-none focus:border-brand-action focus:ring-4 focus:ring-brand-action-soft"
          />
        </div>

        <button
          type="submit"
          disabled={!event && !state.trim()}
          className="inline-flex items-center justify-center gap-2 rounded-xl bg-brand-action px-5 py-2.5 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-50"
        >
          <Search className="h-4 w-4" />
          Search
        </button>
      </form>

      {!searched && (
        <div className="mt-10 rounded-4xl border border-dashed border-border-default bg-surface-sunken p-10 text-center">
          <Search className="mx-auto h-11 w-11 text-text-disabled" />
          <h2 className="mt-5 text-2xl font-bold text-text-primary">
            Choose an event or state to search
          </h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-text-muted">
            At least one filter is required - this isn't a browse-everyone directory.
          </p>
        </div>
      )}

      {searched && (isLoading || isFetching) && (
        <div className="mt-10 flex items-center gap-3 rounded-3xl border border-border-default bg-surface-card p-6 text-sm font-semibold text-text-secondary shadow-sm">
          <Loader2 className="h-5 w-5 animate-spin text-brand-action" />
          Searching...
        </div>
      )}

      {searched && error && (
        <div className="mt-10 rounded-3xl border border-error-failure bg-error-failure-soft p-6 text-sm font-semibold text-error-failure">
          {error.message}
        </div>
      )}

      {searched && !isLoading && !error && results.length === 0 && (
        <div className="mt-10 rounded-4xl border border-dashed border-border-default bg-surface-sunken p-10 text-center">
          <AlertCircle className="mx-auto h-9 w-9 text-text-disabled" />
          <h2 className="mt-4 text-xl font-bold text-text-primary">No matches</h2>
          <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-text-muted">
            No discoverable athletes matched this search. If you believe this
            is wrong, note that talent search also requires{" "}
            {isAcademy ? "this academy account" : "this coach account"} to be
            verified - contact the Shakti team if you're not sure whether
            that's done yet. Discovery deliberately can't tell you which of
            these it is, to avoid revealing anything about who else does or
            doesn't exist in a search.
          </p>
        </div>
      )}

      {searched && !isLoading && results.length > 0 && (
        <div className="mt-8 grid gap-4 sm:grid-cols-2">
          {results.map((athlete) => {
            const alreadyBookmarked = bookmarkedIds.has(athlete.athlete_id);
            const sentName = sentTo[athlete.athlete_id];

            return (
              <div
                key={athlete.athlete_id}
                className="rounded-4xl border border-border-default bg-surface-card p-6 shadow-sm"
              >
                <h2 className="text-xl font-bold text-text-primary">{athlete.full_name}</h2>
                <p className="mt-2 text-sm text-text-muted">
                  {athlete.preferred_event ?? "Event not set"}
                  {athlete.secondary_event ? ` · ${athlete.secondary_event}` : ""}
                  {athlete.state ? ` · ${athlete.state}` : ""}
                </p>

                <div className="mt-5 flex items-center gap-3">
                  <button
                    type="button"
                    onClick={() => createBookmark.mutate(athlete.athlete_id)}
                    disabled={alreadyBookmarked || createBookmark.isPending}
                    className="inline-flex items-center gap-2 rounded-xl border border-border-default px-4 py-2.5 text-sm font-bold text-text-secondary transition hover:border-brand-action hover:text-brand-action disabled:cursor-not-allowed disabled:opacity-50"
                  >
                    <Bookmark className={`h-4 w-4 ${alreadyBookmarked ? "fill-current" : ""}`} />
                    {alreadyBookmarked ? "Bookmarked" : "Bookmark"}
                  </button>

                  {sentName ? (
                    <span className="text-sm font-bold text-success-progress">Request sent</span>
                  ) : (
                    <button
                      type="button"
                      onClick={() => handleConnect(athlete.athlete_id, athlete.full_name)}
                      disabled={requestConnection.isPending}
                      className="inline-flex items-center gap-2 rounded-xl bg-brand-action px-4 py-2.5 text-sm font-bold text-white transition hover:bg-brand-action-hover disabled:cursor-not-allowed disabled:opacity-50"
                    >
                      Request to Connect
                      <ArrowRight className="h-4 w-4" />
                    </button>
                  )}
                </div>

                {requestConnection.isError && requestConnection.variables === athlete.athlete_id && (
                  <p className="mt-2 text-xs font-semibold text-error-failure">
                    {requestConnection.error.message}
                  </p>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
