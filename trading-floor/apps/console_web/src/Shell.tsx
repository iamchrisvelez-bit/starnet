import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { loadMode, sendCommand, type Fetcher } from "./api";
import { ROUTES } from "./routes";
import type { ModePayload } from "./types";

const HALT_BANNER =
  "Positions are unmanaged until Christopher resumes and, if he wants them closed, confirms a separate flatten. KILL does not liquidate. Moonit exits cannot sign while signing is off.";

type Props = {
  fetcher?: Fetcher;
  initialReadToken?: string;
  initialCommandToken?: string;
};

export function Shell({ fetcher = fetch, initialReadToken = "", initialCommandToken = "" }: Props) {
  const [readToken, setReadToken] = useState(initialReadToken);
  const [commandToken, setCommandToken] = useState(initialCommandToken);
  const [mode, setMode] = useState<ModePayload | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!readToken) {
      return;
    }
    let cancelled = false;
    loadMode(fetcher, readToken)
      .then((payload) => {
        if (!cancelled) {
          setMode(payload);
          setError("");
        }
      })
      .catch(() => {
        if (!cancelled) setError("Mode unavailable. No new orders.");
      });
    return () => {
      cancelled = true;
    };
  }, [fetcher, readToken]);

  async function onCommand(action: "kill" | "pause" | "resume") {
    if (!commandToken) {
      setError("Command token required.");
      return;
    }
    try {
      const payload = await sendCommand(fetcher, commandToken, action);
      setMode(payload);
      setError("");
    } catch {
      setError(`${action} refused. No new orders.`);
    }
  }

  const label = mode?.mode ?? "UNKNOWN";
  const badgeClass =
    label === "LIVE"
      ? "bg-neon text-ink"
      : label === "PAPER"
        ? "bg-acid text-ink"
        : "bg-zinc-700 text-white";

  return (
    <div className="min-h-screen bg-ink text-zinc-100">
      <header className="sticky top-0 z-10 border-b border-zinc-800 bg-ink/95 px-4 py-3 backdrop-blur">
        <div className="mx-auto flex max-w-5xl flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <span className="text-sm uppercase tracking-[0.2em] text-zinc-400">Trading Floor</span>
            <span data-testid="mode-badge" className={`rounded px-3 py-2 text-lg font-black ${badgeClass}`}>
              {label}
            </span>
          </div>
          <div className="grid grid-cols-2 gap-2 sm:flex">
            <button
              type="button"
              data-testid="kill"
              className="min-h-12 min-w-24 rounded bg-red-600 px-4 text-base font-black text-white"
              onClick={() => onCommand("kill")}
            >
              KILL
            </button>
            <button
              type="button"
              data-testid="pause"
              className="min-h-12 min-w-24 rounded border border-acid px-4 text-base font-black text-acid"
              onClick={() => onCommand("pause")}
            >
              PAUSE
            </button>
          </div>
        </div>
        {mode?.halted ? (
          <p data-testid="halt-banner" className="mx-auto mt-3 max-w-5xl text-sm text-acid">
            {HALT_BANNER}
          </p>
        ) : null}
        {error ? <p className="mx-auto mt-2 max-w-5xl text-sm text-red-300">{error}</p> : null}
      </header>
      <div className="mx-auto grid max-w-5xl gap-4 px-4 py-4 sm:grid-cols-[12rem_1fr]">
        <nav className="flex gap-2 overflow-x-auto sm:flex-col">
          {ROUTES.map((route) => (
            <NavLink
              key={route.path}
              to={route.path}
              className={({ isActive }) =>
                `whitespace-nowrap rounded px-3 py-2 text-sm ${isActive ? "bg-neon text-ink" : "text-zinc-300"}`
              }
            >
              {route.title}
            </NavLink>
          ))}
        </nav>
        <main>
          <section className="mb-4 grid gap-2 rounded border border-zinc-800 p-3 sm:grid-cols-2">
            <label className="text-xs text-zinc-400">
              Read token
              <input
                className="mt-1 w-full rounded bg-zinc-900 px-2 py-2 text-sm"
                value={readToken}
                onChange={(event) => setReadToken(event.target.value)}
                autoComplete="off"
              />
            </label>
            <label className="text-xs text-zinc-400">
              Command token
              <input
                className="mt-1 w-full rounded bg-zinc-900 px-2 py-2 text-sm"
                value={commandToken}
                type="password"
                onChange={(event) => setCommandToken(event.target.value)}
                autoComplete="off"
              />
            </label>
          </section>
          <Outlet />
        </main>
      </div>
    </div>
  );
}
