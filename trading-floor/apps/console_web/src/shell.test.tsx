import { fireEvent, render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { describe, expect, it } from "vitest";

import { App } from "./App";
import { ROUTES } from "./routes";
import type { ModePayload } from "./types";

const paper: ModePayload = { mode: "PAPER", live_confirmed: false, halted: false, paused: false };

function fetcherFor(payload: ModePayload) {
  const calls: string[] = [];
  const fetcher = async (input: string, init?: RequestInit) => {
    calls.push(`${init?.method ?? "GET"} ${input}`);
    const next = input.endsWith("/kill") ? { ...payload, halted: true } : payload;
    return new Response(JSON.stringify(next), { status: 200 });
  };
  return { fetcher, calls };
}

describe("console shell", () => {
  it.each(ROUTES.map((route) => route.path))("shows PAPER, KILL, and PAUSE on %s", async (path) => {
    const { fetcher } = fetcherFor(paper);
    render(
      <MemoryRouter initialEntries={[path]}>
        <App fetcher={fetcher} initialReadToken="read" initialCommandToken="command" />
      </MemoryRouter>,
    );
    expect(await screen.findByTestId("mode-badge")).toHaveTextContent("PAPER");
    expect(screen.getByTestId("kill")).toBeInTheDocument();
    expect(screen.getByTestId("pause")).toBeInTheDocument();
  });

  it("KILL posts the command and does not call an order route", async () => {
    const { fetcher, calls } = fetcherFor(paper);
    render(
      <MemoryRouter initialEntries={["/orders"]}>
        <App fetcher={fetcher} initialReadToken="read" initialCommandToken="command" />
      </MemoryRouter>,
    );
    await screen.findByTestId("mode-badge");
    fireEvent.click(screen.getByTestId("kill"));
    expect(await screen.findByTestId("halt-banner")).toBeInTheDocument();
    expect(calls.some((call) => call.includes("/api/v1/commands/kill"))).toBe(true);
    expect(calls.some((call) => call.toLowerCase().includes("order") && call.startsWith("POST"))).toBe(false);
  });

  it("renders LIVE in the blue badge", async () => {
    const { fetcher } = fetcherFor({ ...paper, mode: "LIVE", live_confirmed: false });
    render(
      <MemoryRouter initialEntries={["/guards"]}>
        <App fetcher={fetcher} initialReadToken="read" />
      </MemoryRouter>,
    );
    const badge = await screen.findByTestId("mode-badge");
    expect(badge).toHaveTextContent("LIVE");
    expect(badge.className).toContain("bg-neon");
  });
});
