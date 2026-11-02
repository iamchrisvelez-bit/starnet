import type { ModePayload } from "./types";

export type Fetcher = (input: string, init?: RequestInit) => Promise<Response>;

export async function loadMode(fetcher: Fetcher, readToken: string): Promise<ModePayload> {
  const response = await fetcher("/api/v1/mode", {
    headers: { Authorization: `Bearer ${readToken}` },
  });
  if (!response.ok) {
    throw new Error("mode unavailable");
  }
  return response.json() as Promise<ModePayload>;
}

export async function sendCommand(fetcher: Fetcher, commandToken: string, action: "kill" | "pause" | "resume"): Promise<ModePayload> {
  const response = await fetcher(`/api/v1/commands/${action}`, {
    method: "POST",
    headers: { Authorization: `Bearer ${commandToken}` },
  });
  if (!response.ok) {
    throw new Error(`${action} refused`);
  }
  return response.json() as Promise<ModePayload>;
}
